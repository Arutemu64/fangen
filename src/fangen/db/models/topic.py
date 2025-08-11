import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from fangen.cosplay2.models.topic import TopicDTO, TopicFieldDTO, TopicSectionDTO
from fangen.cosplay2.models.vo import ValueType
from fangen.db.models.base import Base

if typing.TYPE_CHECKING:
    from fangen.db.models.request import Request  # noqa


class TopicSection(Base):
    __tablename__ = "topic_sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    title: Mapped[str] = mapped_column()
    order: Mapped[int] = mapped_column()

    fields: Mapped[list["TopicField"]] = relationship(viewonly=True)

    @classmethod
    def from_dto(cls, dto: TopicSectionDTO):
        return TopicSection(
            id=dto.id,
            topic_id=dto.topic_id,
            title=dto.title,
            order=dto.order,
        )


class TopicField(Base):
    __tablename__ = "topic_fields"

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("topic_sections.id"))
    title: Mapped[str] = mapped_column()
    order: Mapped[int] = mapped_column()
    type: Mapped[ValueType] = mapped_column()

    @classmethod
    def from_dto(cls, dto: TopicFieldDTO):
        return TopicField(
            id=dto.id,
            section_id=dto.section_id,
            title=dto.title,
            order=dto.order,
            type=dto.type,
        )


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column()
    url_code: Mapped[str] = mapped_column(unique=True)
    card_code: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column()
    order: Mapped[int] = mapped_column()

    sections: Mapped[list[TopicSection]] = relationship(viewonly=True, order_by=TopicSection.order)
    fields: Mapped[list[TopicField]] = relationship(
        order_by=(TopicSection.order, TopicField.order),
        viewonly=True,
        secondary="topic_sections",
    )
    requests: Mapped[list["Request"]] = relationship(viewonly=True)

    @classmethod
    def from_dto(cls, dto: TopicDTO):
        return Topic(
            id=dto.id,
            event_id=dto.event_id,
            url_code=dto.url_code,
            card_code=dto.card_code,
            title=dto.title,
            order=dto.order,
        )
