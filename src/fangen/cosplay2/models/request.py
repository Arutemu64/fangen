from dataclasses import dataclass

from fangen.cosplay2.models.vo import RequestStatus


@dataclass(slots=True, frozen=True)
class RequestDTO:
    id: int
    topic_id: int
    number: int
    status: RequestStatus
    update_time: str
    user_id: int
    user_title: str
    voting_number: int | None
    voting_title: str | None
