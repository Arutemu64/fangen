from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from fangen.cosplay2.models.plan import PlanNodeDTO
from fangen.cosplay2.models.vo import PlanNodeType
from fangen.db.models import Base, Request, Topic


class PlanNode(Base):
    __tablename__ = "plan"

    uid: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[PlanNodeType] = mapped_column()
    title: Mapped[str] = mapped_column()
    request_length: Mapped[int | None] = mapped_column()
    time_start: Mapped[int | None] = mapped_column()
    time_end: Mapped[int | None] = mapped_column()

    request_id: Mapped[int | None] = mapped_column(ForeignKey("requests.id"))
    request: Mapped[Request | None] = relationship()

    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id"))
    topic: Mapped[Topic | None] = relationship()

    parent_id: Mapped[str | None] = mapped_column(ForeignKey("plan.uid"))
    nodes: Mapped[list["PlanNode"]] = relationship(remote_side=[uid])

    @classmethod
    def from_dto(cls, dto: PlanNodeDTO):
        return PlanNode(
            uid=dto.uid,
            type=dto.type,
            title=dto.title,
            request_length=dto.request_length,
            time_start=dto.time_start,
            time_end=dto.time_end,
            request_id=dto.request_id,
            topic_id=dto.topic_id,
        )
