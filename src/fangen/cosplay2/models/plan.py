import enum
from dataclasses import dataclass


class PlanNodeType(enum.StrEnum):
    PLACE = "place"
    DAY = "day"
    EVENT = "event"
    TOPIC = "topic"
    REQUEST = "request"
    BREAK = "break"


@dataclass(frozen=True, slots=True, kw_only=True)
class PlanNodeDTO:
    uid: str
    type: PlanNodeType
    title: str

    request_length: int | None = None
    time_start: int | None = None
    time_end: int | None = None

    request_id: int | None = None
    topic_id: int | None = None

    nodes: list["PlanNodeDTO"] | None = None
