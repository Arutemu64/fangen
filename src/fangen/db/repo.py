from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from fangen.db.models import Request
from fangen.db.models.node import PlanNode


def get_plan_nodes(session: Session) -> Sequence[PlanNode]:
    stmt = select(PlanNode).options(
        joinedload(PlanNode.nodes),
        joinedload(PlanNode.topic),
        joinedload(PlanNode.request).joinedload(Request.values),
    )
    return session.scalars(stmt).unique().all()
