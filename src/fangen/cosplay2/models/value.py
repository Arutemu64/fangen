from dataclasses import dataclass

from fangen.cosplay2.models.vo import ValueType


@dataclass(slots=True, frozen=True)
class RequestValueDTO:
    request_id: int
    title: str
    type: ValueType
    value: str
