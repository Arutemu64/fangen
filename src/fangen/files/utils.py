import os
from pathlib import Path

from fangen.cosplay2.models.vo import ValueType

FILE_VALUE_TYPES = {ValueType.FILE, ValueType.IMAGE}


def find_file_by_id(output_dir: Path, value_id: int) -> Path | None:
    str_id = str(value_id)
    for entry in os.scandir(output_dir):
        if entry.is_file() and entry.name.startswith(str_id + "."):
            return Path(entry.path)  # Return as Path for compatibility
    return None
