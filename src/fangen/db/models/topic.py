from sqlalchemy.orm import mapped_column, Mapped

from fangen.cosplay2.models.topic import TopicDTO
from fangen.db.models.base import Base


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column()
    card_code: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column()

    @classmethod
    def from_dto(cls, dto: TopicDTO):
        return Topic(
            id=dto.id,
            event_id=dto.event_id,
            card_code=dto.card_code,
            title=dto.title,
        )
