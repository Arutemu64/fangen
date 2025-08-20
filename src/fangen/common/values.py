import datetime
import json
from dataclasses import dataclass

from fangen.db.models import RequestValue


@dataclass(frozen=True, slots=True)
class ImageValue:
    filename: str


@dataclass(frozen=True, slots=True, kw_only=True)
class FileValue:
    # Hosted on Cosplay2
    filename: str | None = None
    filesize: int | None = None
    fileext: str | None = None

    # Link
    link: str | None = None


def parse_checkbox_value(value: RequestValue) -> bool:
    return value.value == "YES"


def parse_image_value(value: RequestValue) -> ImageValue:
    image_info = json.loads(value.value)
    filename = image_info["filename"]
    return ImageValue(filename)


def parse_file_value(value: RequestValue) -> FileValue:
    file_info = json.loads(value.value)
    if file_info.get("filename"):
        return FileValue(
            filename=file_info["filename"],
            filesize=file_info["filesize"],
            fileext=file_info["fileext"],
        )
    return FileValue(
        link=file_info["link"],
    )


def parse_duration_value(value: RequestValue) -> datetime.timedelta:
    return datetime.timedelta(minutes=float(value.value))
