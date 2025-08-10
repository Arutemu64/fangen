from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fangen.cosplay2.models.request import RequestStatus, RequestDTO
from fangen.db.models.base import Base
from fangen.db.models.topic import Topic
from fangen.db.models.value import RequestValue


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    status: Mapped[RequestStatus] = mapped_column()
    number: Mapped[int] = mapped_column()
    user_title: Mapped[str] = mapped_column()
    voting_number: Mapped[int | None] = mapped_column()
    voting_title: Mapped[int | None] = mapped_column()

    topic: Mapped[Topic] = relationship(viewonly=True)
    values: Mapped[list[RequestValue]] = relationship(viewonly=True)

    @classmethod
    def from_dto(cls, dto: RequestDTO):
        return Request(
            id=dto.id,
            topic_id=dto.topic_id,
            status=dto.status,
            number=dto.number,
            user_title=dto.user_title,
            voting_number=dto.voting_number,
            voting_title=dto.voting_title,
        )
