import enum
from dataclasses import dataclass


class RequestStatus(enum.StrEnum):
    PENDING = "pending"
    WAITING = "waiting"
    MATERIALS = "materials"
    REVIEW = "review"
    APPROVED = "approved"
    DISAPPROVED = "disapproved"


@dataclass(slots=True, frozen=True)
class RequestDTO:
    id: int
    topic_id: int
    number: int
    status: RequestStatus
    user_id: int
    user_title: str
    voting_number: int | None
    voting_title: str | None
