from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from fangen.db.models import Request, Topic, TopicSection, TopicField
from fangen.db.models.node import PlanNode


def get_plan_nodes(session: Session) -> Sequence[PlanNode]:
    stmt = (
        select(PlanNode)
        .order_by(PlanNode.time_start)
        .options(
            joinedload(PlanNode.nodes),
            joinedload(PlanNode.topic),
            joinedload(PlanNode.request).joinedload(Request.values),
        )
    )
    return session.scalars(stmt).unique().all()


def get_topics(session: Session) -> Sequence[Topic]:
    stmt = (
        select(Topic)
        .order_by(Topic.order)
        .options(
            joinedload(Topic.fields),
            joinedload(Topic.requests).joinedload(Request.values),
        )
    )
    return session.scalars(stmt).unique().all()
