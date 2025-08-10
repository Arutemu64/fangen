import enum
from dataclasses import dataclass


class ValueType(enum.StrEnum):
    TEXT = "text"
    PHONE = "phone"
    TEXTAREA = "textarea"
    LINK = "link"
    CHECKBOX = "checkbox"
    USER = "user"
    DURATION = "duration"
    IMAGE = "image"
    SELECT = "select"
    NUM = "num"
    FILE = "file"


@dataclass(slots=True, frozen=True)
class RequestValueDTO:
    request_id: int
    title: str
    type: ValueType
    value: str
