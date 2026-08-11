from dataclasses import dataclass

from fangen.cosplay2.models.vo import ValueType


@dataclass(slots=True, frozen=True)
class TopicDTO:
    id: int
    event_id: int
    url_code: str
    card_code: str
    title: str
    order: int


@dataclass(slots=True, frozen=True)
class TopicSectionDTO:
    id: int
    topic_id: int
    title: str
    order: int


@dataclass(slots=True, frozen=True)
class TopicFieldDTO:
    id: int
    section_id: int
    title: str
    order: int
    type: ValueType


@dataclass(frozen=True, slots=True)
class TopicWithFieldsDTO:
    topic: TopicDTO
    topic_sections: list[TopicSectionDTO]
    topic_fields: list[TopicFieldDTO]
