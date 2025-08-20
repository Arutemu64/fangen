import enum
import shutil
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
from fangen.files.utils import FILE_VALUE_TYPES, find_file_by_id


class DownloadStatus(enum.StrEnum):
    OK = "ok"
    FAIL = "fail"
    SKIP = "skip"


@dataclass(slots=True, frozen=True)
class DownloadResult:
    status: DownloadStatus
    filename: str
    request_title: str
    value_title: str
    link: str

    def __str__(self):
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


def download_value_file(
    value: RequestValue, request: Request, output_dir: Path, config: Config
) -> DownloadResult:
    def fail_result(filename: str, link: str = "Не приложен"):
        return DownloadResult(
            status=DownloadStatus.FAIL,
            filename=filename,
            request_title=request.voting_title,
            value_title=value.title,
            link=link,
        )

    internal_filename = f"{value.id}.*"

    if value.value is None:
        return fail_result(internal_filename)

    link = parse_download_link(value, request)
    if not link:
        return fail_result(internal_filename)

    existing_file = find_file_by_id(output_dir, value.id)
    if existing_file:
        file_mtime = datetime.fromtimestamp(existing_file.stat().st_mtime)
        update_time = datetime.strptime(request.update_time, "%d.%m.%y %H:%M")
        if file_mtime > update_time:
            return DownloadResult(
                status=DownloadStatus.OK,
                filename=existing_file.name,
                request_title=request.voting_title,
                value_title=value.title,
                link=link,
            )

    ydl_config = {"outtmpl": f"{output_dir}/%(title)s.%(ext)s", "quiet": True}
    with yt_dlp.YoutubeDL(ydl_config) as ydl:
        try:
            info = ydl.extract_info(link, download=False)
            save_path = Path(ydl.prepare_filename(info).lower())
            ext = save_path.suffix
            internal_filename = f"{value.id}{ext}"
        except (DownloadError, TypeError):
            return fail_result(internal_filename, link)

        if (
            value.title in config.skip_fields
            or ext.lstrip(".") not in config.allowed_exts
        ):
            return DownloadResult(
                status=DownloadStatus.SKIP,
                filename=internal_filename,
                request_title=request.voting_title,
                value_title=value.title,
                link=link,
            )

        if not config.dry_run:
            try:
                ydl.download([link])
                shutil.move(save_path, output_dir / internal_filename)
            except DownloadError:
                return fail_result(internal_filename, link)

    return DownloadResult(
        status=DownloadStatus.OK,
        filename=internal_filename,
        request_title=request.voting_title,
        value_title=value.title,
        link=link,
    )


def download_files(output_dir: Path, session: Session, config: Config) -> None:
    print("💻 Загружаем заявки...")
    requests = get_approved_requests(session)
    print("💾 Начинаем проверку и скачивание файлов...")
    results: list[DownloadResult] = []

    for request in requests:
        for value in (
            v
            for v in request.values
            if v.type in FILE_VALUE_TYPES and v.title not in config.skip_fields
        ):
            result = download_value_file(value, request, output_dir, config)
            print(str(result))
            results.append(result)

    log_file = output_dir / "log.txt"
    with log_file.open("w", encoding="utf-8") as f:
        for status in [DownloadStatus.FAIL, DownloadStatus.SKIP, DownloadStatus.OK]:
            f.write(f"\n--------[{status.name}]--------\n")
            f.writelines(f"{r}\n" for r in results if r.status == status)

    print(
        "🎉 Готово! Проверьте логи и скачайте файлы со статусом [FAIL] вручную. "
        "Назовите их как указанно в логе."
    )
