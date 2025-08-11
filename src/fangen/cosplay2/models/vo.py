import enum


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


class RequestStatus(enum.StrEnum):
    PENDING = "pending"
    WAITING = "waiting"
    MATERIALS = "materials"
    REVIEW = "review"
    APPROVED = "approved"
    DISAPPROVED = "disapproved"


class PlanNodeType(enum.StrEnum):
    PLACE = "place"
    DAY = "day"
    EVENT = "event"
    TOPIC = "topic"
    REQUEST = "request"
    BREAK = "break"
