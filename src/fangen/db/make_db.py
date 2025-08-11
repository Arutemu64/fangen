from pathlib import Path

from rich import print

from fangen.cosplay2.client import Cosplay2Client
from fangen.cosplay2.models.plan import PlanNodeDTO
from fangen.db.factory import get_session, create_db
from fangen.db.models import Topic, Request, RequestValue
from fangen.db.models.node import PlanNode


def make_db(client: Cosplay2Client, db_path: Path):
    print("🌐 Начинаем наполнение базы данных...")
    create_db(db_path=db_path)
    session = get_session(db_path=db_path)

    with session:
        # Seed topics
        print("💾 Сохраняем номинации...")
        topics = client.get_topics()
        session.add_all([Topic.from_dto(topic) for topic in topics])
        session.flush()
        print(f"💾 Сохранено {len(topics)} номинаций")

        # Seed requests
        print("💾 Сохраняем заявки...")
        requests = client.get_all_requests()
        session.add_all([Request.from_dto(req) for req in requests])
        session.flush()
        print(f"💾 Сохранено {len(requests)} заявок")

        # Seed values
        print("💾 Сохраняем данные...")
        values = client.get_all_values()
        session.add_all(RequestValue.from_dto(val) for val in values)
        session.flush()
        print(f"💾 Сохранено {len(values)} строк данных")

        # Seed plan
        print("💾 Сохраняем расписание...")
        plan = client.get_plan()

        def proceed_node(node: PlanNodeDTO, parent_id: str | None = None):
            node_orm = PlanNode.from_dto(node)
            if parent_id:
                node_orm.parent_id = parent_id
            session.add(node_orm)
            session.flush([node_orm])
            if node.nodes:
                for child_node in node.nodes:
                    proceed_node(child_node, node_orm.uid)

        for node in plan:
            proceed_node(node)

        # Commit
        session.commit()
        print(f"💾 Готово! База данных располагается тут: {db_path.absolute()}")
