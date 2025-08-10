from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class TopicDTO:
    id: int
    event_id: int
    card_code: str
    title: str
