from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from fangen.cosplay2.models.vo import RequestStatus
from fangen.db.models import Request, Topic
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


def get_topics_with_approved_requests(session: Session) -> Sequence[Topic]:
    stmt = select(Topic).options(
        joinedload(Topic.fields),
        joinedload(
            Topic.requests.and_(Request.status == RequestStatus.APPROVED)
        ).joinedload(Request.values),
    )
    return session.scalars(stmt).unique().all()


def get_approved_requests(session: Session) -> Sequence[Request]:
    stmt = (
        select(Request)
        .where(Request.status == RequestStatus.APPROVED)
        .options(joinedload(Request.values))
    )
    return session.scalars(stmt).unique().all()
