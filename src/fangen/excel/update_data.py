import re
from pathlib import Path

from openpyxl import Workbook
from rich import print
from sqlalchemy.orm import Session

from fangen.common.data import parse_request
from fangen.config import Config
from fangen.cosplay2.models.vo import PlanNodeType
from fangen.db.repo import get_plan_nodes, get_topics_with_approved_requests
from fangen.excel.formatting import EVEN_ROW_FILL, apply_final_formatting
from fangen.excel.utils import check_excel_file


def make_data(filepath: Path, session: Session, config: Config) -> None:
    if filepath.exists():
        check_excel_file(filepath)
    wb = Workbook()

    # Лист с общими данными
    print("💻 Заполняем сводный лист...")
    ws = wb.active
    ws.title = "Сводный"
    ws.freeze_panes = "B1"
    plan_nodes = get_plan_nodes(session)
    requests = [
        node.request
        for node in plan_nodes
        if node.type is PlanNodeType.REQUEST and node.request is not None
    ]
    headers = ["info"]
    seen = set()
    for request in requests:
        for value in request.values:
            if value.title not in seen:
                seen.add(value.title)
                headers.append(value.title)
    ws.append(headers)
    current_row_index = 2
    for request in requests:
        current_row = ws[current_row_index]
        data = parse_request(request)
        for cell, header in zip(current_row, headers, strict=False):
            if isinstance(header, str):
                cell.value = str(data.get(header) or "—")
            if current_row_index % 2 == 0:
                cell.fill = EVEN_ROW_FILL
        current_row_index += 1
    print("🧹 Наводим красоту...")
    apply_final_formatting(ws, max_cell_length=config.max_cell_length, freeze_cell="B2")

    # Листы под каждый раздел
    print("💻 Заполняем листы разделов...")
    topics = get_topics_with_approved_requests(session)
    for topic in topics:
        print(f"""📄 Заполняем лист раздела '{topic.title}'...""")
        title = re.sub(r"[\/\\\?\*\:\[\]]", " ", topic.title)[:30]
        ws = wb.create_sheet(title=title)

        headers = [field.title for field in topic.fields]
        ws.append(headers)

        for request in topic.requests:
            current_row_index = topic.requests.index(request) + 2
            data = parse_request(request)
            current_row = ws[current_row_index]
            for cell, header in zip(current_row, headers, strict=False):
                cell.value = str(data.get(header, ""))
                if current_row_index % 2 == 0:
                    cell.fill = EVEN_ROW_FILL
    print("🧹 Наводим красоту...")
    for ws in wb.worksheets[1:]:
        apply_final_formatting(ws, max_cell_length=config.max_cell_length)

    wb.save(filepath)
    print(f"💾 Файл сохранен по пути {filepath.absolute()}")
