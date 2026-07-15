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
from fangen.db.models import RequestValue
from fangen.db.repo import get_approved_requests, get_plan_nodes
from fangen.files.utils import build_file_index, iter_file_values, write_log

ILLEGAL_CHARS = r'[<>:"/\\|?*\x00-\x1F]'
REPLACEMENT_CHAR = "_"
# Path components that would escape or alias the output directory.
UNSAFE_PARTS = {"", ".", ".."}


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

    def __str__(self) -> str:
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


def resolve_destination(raw_path: str, output_dir: Path) -> Path:
    """Turn a templated path into a safe destination under ``output_dir``.

    Each component is sanitized, and components that would escape the tree
    (``..``, ``.`` or empty) are dropped so the result always stays inside
    ``output_dir``.
    """
    normalized = raw_path.replace("\\", "/")
    parts = [
        sanitized
        for part in normalized.split("/")
        if (sanitized := sanitize_value(part)) not in UNSAFE_PARTS
    ]
    return output_dir.joinpath(*parts)


def move_value_file(
    value: RequestValue,
    request_data: dict,
    extra_data: dict,
    src: Path | None,
    output_dir: Path,
    config: Config,
    dictionary: dict,
) -> MoveResult:
    request_title = request_data.get("info")

    if not src:
        # File not found but it was actually required
        return MoveResult(
            MoveStatus.NOT_FOUND, f"{value.id}.*", request_title, value.title
        )

    internal_filename = src.name
    ext = src.suffix
    if ext.lstrip(".") not in config.allowed_exts:
        return MoveResult(
            MoveStatus.SKIP, internal_filename, request_title, value.title
        )

    data = dict(request_data)
    data.update(extra_data)
    data["title"] = (data.get("title") or "[notitle]")[: config.max_title_length]
    data["info"] = (data.get("info") or "[noinfo]")[: config.max_title_length]
    data = sanitize_data(data)

    raw_path = format_template(config.filename_template, data, dictionary) + (
        f"_{value.id}{ext}"
    )
    dst = resolve_destination(raw_path, output_dir)

    if not dst.exists() and not config.dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)

    return MoveResult(MoveStatus.OK, raw_path, request_title, value.title)


def move_files(
    input_dir: Path, output_dir: Path, session: Session, config: Config
) -> None:
    with config.dict_path.open(encoding="utf-8") as f:
        dictionary = json.load(f)

    print("💻 Загружаем расписание и данные...")
    if config.stage_mode:
        plan_nodes = get_plan_nodes(session)
        requests = [
            node.request
            for node in plan_nodes
            if node.type is PlanNodeType.REQUEST and node.request is not None
        ]
    else:
        requests = get_approved_requests(session)

    file_index = build_file_index(input_dir)
    results: list[MoveResult] = []

    for idx, request in enumerate(
        track(requests, description="🗃️ Проверяем и копируем файлы..."), 1
    ):
        request_data = parse_request(request)
        for value in iter_file_values(request, config):
            extra_data = {"n": f"{idx:03}", "value_title": value.title}
            result = move_value_file(
                value,
                request_data,
                extra_data,
                file_index.get(value.id),
                output_dir,
                config,
                dictionary,
            )
            print(str(result))
            results.append(result)

    write_log(
        output_dir / "log.txt",
        [(r.status, str(r)) for r in results],
        [MoveStatus.NOT_FOUND, MoveStatus.SKIP, MoveStatus.OK],
    )

    print(
        "🎉 Готово! Проверьте логи и разберитесь, что произошло с файлами [NOT FOUND]."
    )
