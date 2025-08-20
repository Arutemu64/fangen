import enum
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from rich import print
from rich.progress import track
from sqlalchemy.orm import Session

from fangen.common.data import parse_request
from fangen.common.utils import format_template
from fangen.config import Config
from fangen.cosplay2.models.vo import PlanNodeType
from fangen.db.models import Request, RequestValue
from fangen.db.repo import get_approved_requests, get_plan_nodes
from fangen.files.utils import FILE_VALUE_TYPES, find_file_by_id

ILLEGAL_CHARS = r'[<>:"/\\|?*\x00-\x1F]'
REPLACEMENT_CHAR = "_"


class MoveStatus(enum.StrEnum):
    OK = "ok"
    SKIP = "skip"
    NOT_FOUND = "not found"


@dataclass(slots=True, frozen=True)
class MoveResult:
    status: MoveStatus
    filename: str
    request_title: str | None
    value_title: str

    def __str__(self):
        return (
            f"[{self.status.upper()}] {self.filename} "
            f"| {self.value_title} > {self.request_title}"
        )


def sanitize_value(value: str) -> str:
    cleaned = re.sub(ILLEGAL_CHARS, REPLACEMENT_CHAR, value)
    cleaned = re.sub(rf"{re.escape(REPLACEMENT_CHAR)}+", REPLACEMENT_CHAR, cleaned)
    return cleaned.strip()


def sanitize_data(d: dict) -> dict:
    sanitized = {}
    for k, v in d.items():
        if isinstance(v, str):
            sanitized[k] = sanitize_value(v)
        elif isinstance(v, dict):
            sanitized[k] = sanitize_data(v)
        else:
            sanitized[k] = v
    return sanitized


def move_value_file(
    value: RequestValue,
    request: Request,
    extra_data: dict,
    input_dir: Path,
    output_dir: Path,
    config: Config,
    dictionary: dict,
) -> MoveResult:
    internal_filename = f"{value.id}.*"

    src = find_file_by_id(input_dir, value.id)
    if not src and value.title not in config.skip_fields:
        # File not found but it was actually required
        return MoveResult(
            MoveStatus.NOT_FOUND, internal_filename, request.voting_title, value.title
        )

    internal_filename = src.name

    # File is not required
    if value.title in config.skip_fields:
        return MoveResult(
            MoveStatus.SKIP, internal_filename, request.voting_title, value.title
        )

    data = parse_request(request)
    data.update(extra_data)
    data["title"] = (data.get("title") or "[notitle]")[: config.max_title_length]
    data["info"] = (data.get("info") or "[noinfo]")[: config.max_title_length]
    data = sanitize_data(data)

    ext = src.suffix
    if ext.lstrip(".") not in config.allowed_exts:
        return MoveResult(
            MoveStatus.SKIP, internal_filename, request.voting_title, value.title
        )

    raw_path = (
        format_template(config.filename_template, data, dictionary)
        + f"_{value.id}{ext}"
    )
    normalized = raw_path.replace("\\", "/")
    parts = normalized.split("/")
    parts = [sanitize_value(p) for p in parts]
    dst = output_dir.joinpath(*parts)

    if not dst.exists() and not config.dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)

    return MoveResult(MoveStatus.OK, raw_path, request.voting_title, value.title)


def move_files(
    input_dir: Path, output_dir: Path, session: Session, config: Config
) -> None:
    with config.dict_path.open(encoding="utf-8") as f:
        dictionary = json.load(f)

    print("💻 Загружаем расписание и данные...")
    if config.stage_mode:
        plan_nodes = get_plan_nodes(session)
        requests = [
            node.request for node in plan_nodes if node.type is PlanNodeType.REQUEST
        ]
    else:
        requests = get_approved_requests(session)

    results: list[MoveResult] = []

    for idx, request in enumerate(
        track(requests, description="🗃️ Проверяем и копируем файлы..."), 1
    ):
        for value in (
            v
            for v in request.values
            if v.type in FILE_VALUE_TYPES and v.title not in config.skip_fields
        ):
            extra_data = {"n": f"{idx:03}", "value_title": value.title}
            value: RequestValue
            result = move_value_file(
                value,
                request,
                extra_data,
                input_dir,
                output_dir,
                config,
                dictionary,
            )
            print(str(result))
            results.append(result)

    log_file = output_dir / "log.txt"
    with log_file.open("w", encoding="utf-8") as f:
        for status in [MoveStatus.NOT_FOUND, MoveStatus.SKIP, MoveStatus.OK]:
            f.write(f"\n--------[{status.name}]--------\n")
            f.writelines(f"{r}\n" for r in results if r.status == status)

    print("🎉 Готово! Проверьте логи и разберитесь, что произошло с файлами [FAIL].")
