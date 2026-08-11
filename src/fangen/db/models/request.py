from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# mapped_column() de-stringifies this annotation via eval() at class-body
# time, so it must be a real (non-TYPE_CHECKING) import.
from fangen.cosplay2.models.vo import RequestStatus  # noqa: TC001
from fangen.db.models.base import Base
from fangen.db.models.value import RequestValue

if TYPE_CHECKING:
    from fangen.cosplay2.models.request import RequestDTO
    from fangen.db.models.topic import Topic


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    status: Mapped[RequestStatus] = mapped_column()
    update_time: Mapped[str] = mapped_column()
    number: Mapped[int] = mapped_column()
    user_title: Mapped[str] = mapped_column()
    voting_number: Mapped[int | None] = mapped_column()
    voting_title: Mapped[str | None] = mapped_column()

    topic: Mapped[Topic] = relationship(viewonly=True)
    values: Mapped[list[RequestValue]] = relationship(
        viewonly=True, order_by=RequestValue.id
    )

    @classmethod
    def from_dto(cls, dto: RequestDTO) -> Request:
        return Request(
            id=dto.id,
            topic_id=dto.topic_id,
            status=dto.status,
            update_time=dto.update_time,
            number=dto.number,
            user_title=dto.user_title,
            voting_number=dto.voting_number,
            voting_title=dto.voting_title,
        )
