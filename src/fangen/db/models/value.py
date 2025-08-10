import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fangen.cosplay2.models.value import ValueType, RequestValueDTO
from fangen.db.models.base import Base

if typing.TYPE_CHECKING:
    from fangen.db.models import Request  # noqa


class RequestValue(Base):
    __tablename__ = "values"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"))
    title: Mapped[str] = mapped_column()
    type: Mapped[ValueType] = mapped_column()
    value: Mapped[str] = mapped_column()

    request: Mapped["Request"] = relationship(viewonly=True)

    @classmethod
    def from_dto(cls, dto: RequestValueDTO):
        return RequestValue(
            request_id=dto.request_id,
            title=dto.title,
            type=dto.type,
            value=dto.value,
        )
