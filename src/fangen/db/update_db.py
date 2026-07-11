from pathlib import Path

from rich import print
from rich.progress import track

from fangen.cosplay2.client import Cosplay2Client
from fangen.cosplay2.models.plan import PlanNodeDTO
from fangen.db.factory import create_db, get_session
from fangen.db.models import Request, RequestValue, Topic, TopicField, TopicSection
from fangen.db.models.node import PlanNode


def make_db(client: Cosplay2Client, db_path: Path) -> None:
    print("🌐 Начинаем наполнение базы данных...")
    create_db(db_path=db_path)
    session = get_session(db_path=db_path)

    with session:
        # Seed topics
        print("💾 Сохраняем разделы...")
        topics = client.get_list()
        session.add_all([Topic.from_dto(topic) for topic in topics])
        print(f"💾 Сохранено {len(topics)} разделов")

        for topic in track(topics, description="💾 Сохраняем поля разделов..."):
            with_fields = client.get_with_fields(topic_url_code=topic.url_code)
            session.add_all(
                [
                    TopicSection.from_dto(topic_section)
                    for topic_section in with_fields.topic_sections
                ]
            )
            session.add_all(
                [
                    TopicField.from_dto(topic_field)
                    for topic_field in with_fields.topic_fields
                ]
            )

        # Seed requests
        print("💾 Сохраняем заявки...")
        requests = client.get_all_requests()
        session.add_all([Request.from_dto(req) for req in requests])
        session.flush()
        print(f"💾 Сохранено {len(requests)} заявок")

        # Seed values
        print("💾 Сохраняем данные из заявок...")
        values = client.get_all_values()
        session.add_all(RequestValue.from_dto(val) for val in values)
        session.flush()
        print(f"💾 Сохранено {len(values)} строк данных из заявок")

        # Seed plan
        print("💾 Сохраняем расписание...")
        plan = client.get_plan()

        def proceed_node(node: PlanNodeDTO, parent_id: str | None = None) -> None:
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
