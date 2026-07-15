import os
from collections.abc import Iterable, Iterator, Sequence
from enum import StrEnum
from pathlib import Path

from fangen.config import Config
from fangen.cosplay2.models.vo import ValueType
from fangen.db.models import Request, RequestValue

FILE_VALUE_TYPES = {ValueType.FILE, ValueType.IMAGE}


def iter_file_values(request: Request, config: Config) -> Iterator[RequestValue]:
    """Yield the file/image values of a request that should be processed."""
    for value in request.values:
        if value.type in FILE_VALUE_TYPES and value.title not in config.skip_fields:
            yield value


def build_file_index(directory: Path) -> dict[int, Path]:
    """Map ``value.id`` -> path for every ``<id>.<ext>`` file in ``directory``.

    Scans the directory once instead of walking it per lookup.
    """
    index: dict[int, Path] = {}
    for entry in os.scandir(directory):
        if not entry.is_file():
            continue
        prefix, dot, _ = entry.name.partition(".")
        if dot and prefix.isdigit():
            index[int(prefix)] = Path(entry.path)
    return index


def write_log(
    log_file: Path,
    entries: Iterable[tuple[StrEnum, str]],
    order: Sequence[StrEnum],
) -> None:
    """Write ``(status, line)`` entries grouped by status in the given order."""
    entries = list(entries)
    with log_file.open("w", encoding="utf-8") as f:
        for status in order:
            f.write(f"\n--------[{status.name}]--------\n")
            for entry_status, line in entries:
                if entry_status == status:
                    f.write(f"{line}\n")
