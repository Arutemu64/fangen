import tomllib
from dataclasses import dataclass
from pathlib import Path

from adaptix import Retort


@dataclass(slots=True, frozen=True)
class Config:
    # General config
    email: str
    password: str
    event_name: str
    db_path: Path
    dict_path: Path

    # Excel
    max_cell_length: int

    # Files
    skip_fields: set[str]
    dry_run: bool

    # Downloader
    files_folder: Path

    # Mover
    move_folder: Path
    stage_mode: bool
    allowed_exts: set[str]
    filename_template: str
    max_title_length: int


def load_config(path: Path) -> Config:
    retort = Retort()
    with path.open("rb") as f:
        data = tomllib.load(f)
        return retort.load(data, Config)
