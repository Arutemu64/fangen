import tomllib
from dataclasses import dataclass
from pathlib import Path

from adaptix import Retort


@dataclass(slots=True, frozen=True)
class Config:
    email: str
    password: str
    event_name: str
    dict_path: Path
    db_path: Path = Path("./database.db")


def load_config(path: Path) -> Config:
    retort = Retort()
    with open(path, "rb") as f:
        data = tomllib.load(f)
        return retort.load(data, Config)
