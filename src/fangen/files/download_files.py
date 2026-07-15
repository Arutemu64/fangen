import enum
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yt_dlp
from rich import print
from sqlalchemy.orm import Session
from yt_dlp import DownloadError

from fangen.common.utils import build_cosplay2_file_link, build_cosplay2_image_link
from fangen.common.values import parse_file_value, parse_image_value
from fangen.config import Config
from fangen.cosplay2.models.vo import ValueType
from fangen.db.models import Request, RequestValue
from fangen.db.repo import get_approved_requests
from fangen.files.utils import build_file_index, iter_file_values, write_log


class DownloadStatus(enum.StrEnum):
    OK = "ok"
    FAIL = "fail"
    SKIP = "skip"


@dataclass(slots=True, frozen=True)
class DownloadResult:
    status: DownloadStatus
    filename: str
    request_title: str | None
    value_title: str
    link: str

    def __str__(self) -> str:
        return (
            f"[{self.status.upper()}] {self.filename} | "
            f"{self.value_title} > {self.request_title} | {self.link}"
        )


def parse_download_link(value: RequestValue, request: Request) -> str | None:
    if value.type == ValueType.IMAGE:
        filename = parse_image_value(value).filename
        return build_cosplay2_image_link(request.topic.event_id, request.id, filename)
    if value.type == ValueType.FILE:
        file_value = parse_file_value(value)
        return (
            build_cosplay2_file_link(
                request.topic.event_id, request.id, file_value.filename
            )
            if file_value.filename
            else file_value.link
        )
    return None


def _is_up_to_date(file: Path, update_time: str) -> bool:
    """Whether ``file`` is newer than the request's last update.

    Returns ``False`` on an unparseable ``update_time`` so the file is
    re-downloaded rather than trusted blindly.
    """
    try:
        parsed = datetime.strptime(update_time, "%d.%m.%y %H:%M")
    except (ValueError, TypeError):
        return False
    return datetime.fromtimestamp(file.stat().st_mtime) > parsed


def _remove_files_by_id(directory: Path, value_id: int) -> None:
    """Delete any ``<value_id>.<ext>`` file(s), regardless of extension."""
    prefix = f"{value_id}."
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.startswith(prefix):
            Path(entry.path).unlink(missing_ok=True)


def download_value_file(
    value: RequestValue,
    request: Request,
    output_dir: Path,
    config: Config,
    existing_files: dict[int, Path],
) -> DownloadResult:
    def result(
        status: DownloadStatus, filename: str, link: str = "Не приложен"
    ) -> DownloadResult:
        return DownloadResult(
            status=status,
            filename=filename,
            request_title=request.voting_title,
            value_title=value.title,
            link=link,
        )

    internal_filename = f"{value.id}.*"

    if value.value is None:
        return result(DownloadStatus.FAIL, internal_filename)

    try:
        link = parse_download_link(value, request)
    except (KeyError, ValueError, json.JSONDecodeError):
        return result(DownloadStatus.FAIL, internal_filename)
    if not link:
        return result(DownloadStatus.FAIL, internal_filename)

    existing_file = existing_files.get(value.id)
    if existing_file and _is_up_to_date(existing_file, request.update_time):
        return result(DownloadStatus.OK, existing_file.name, link)

    # yt-dlp names the file after the value id so lookups stay deterministic.
    ydl_config = {"outtmpl": f"{output_dir}/{value.id}.%(ext)s", "quiet": True}
    with yt_dlp.YoutubeDL(ydl_config) as ydl:
        try:
            info = ydl.extract_info(link, download=False)
            ext = Path(ydl.prepare_filename(info)).suffix.lower()
        except (DownloadError, TypeError):
            return result(DownloadStatus.FAIL, internal_filename, link)

        internal_filename = f"{value.id}{ext}"

        if ext.lstrip(".") not in config.allowed_exts:
            return result(DownloadStatus.SKIP, internal_filename, link)

        if config.dry_run:
            return result(DownloadStatus.OK, internal_filename, link)

        # Drop any stale file for this id (e.g. a different extension) so
        # yt-dlp does not skip the download believing it already exists.
        _remove_files_by_id(output_dir, value.id)
        try:
            dl_info = ydl.extract_info(link, download=True)
        except (DownloadError, OSError):
            return result(DownloadStatus.FAIL, internal_filename, link)

        downloaded = dl_info.get("requested_downloads") if dl_info else None
        save_path = (
            Path(downloaded[0]["filepath"])
            if downloaded
            else Path(ydl.prepare_filename(dl_info))
        )
        internal_filename = save_path.name

    return result(DownloadStatus.OK, internal_filename, link)


def download_files(output_dir: Path, session: Session, config: Config) -> None:
    print("💻 Загружаем заявки...")
    requests = get_approved_requests(session)
    print("💾 Начинаем проверку и скачивание файлов...")
    existing_files = build_file_index(output_dir)
    results: list[DownloadResult] = []

    for request in requests:
        for value in iter_file_values(request, config):
            result = download_value_file(
                value, request, output_dir, config, existing_files
            )
            print(str(result))
            results.append(result)

    write_log(
        output_dir / "log.txt",
        [(r.status, str(r)) for r in results],
        [DownloadStatus.FAIL, DownloadStatus.SKIP, DownloadStatus.OK],
    )

    print(
        "🎉 Готово! Проверьте логи и скачайте файлы со статусом [FAIL] вручную. "
        "Назовите их как указанно в логе."
    )
