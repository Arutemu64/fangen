import tomllib
from dataclasses import dataclass
from pathlib import Path

from adaptix import Retort

# NOTE: `Path` must be imported at runtime, not under `TYPE_CHECKING`. adaptix
# resolves the `Config` annotations at runtime via `get_type_hints` when
# building the loader, so every annotated type has to be a real name in this
# module's namespace.


@dataclass(slots=True, frozen=True)
class Config:
    # General config
    api_key: str
    api_secret: str
    event_name: str
    db_path: Path
    dict_path: Path

    # Excel
    max_cell_length: int

    # Files
    skip_fields: set[str]
    dry_run: bool

    # Mover
    stage_mode: bool
    allowed_exts: set[str]
    filename_template: str
    max_title_length: int


def load_config(path: Path) -> Config:
    retort = Retort()
    with path.open("rb") as f:
        data = tomllib.load(f)
        return retort.load(data, Config)
