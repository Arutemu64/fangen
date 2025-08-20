import datetime

from fangen.common.utils import build_cosplay2_file_link, build_cosplay2_image_link
from fangen.common.values import (
    parse_checkbox_value,
    parse_duration_value,
    parse_file_value,
    parse_image_value,
)
from fangen.cosplay2.models.vo import PlanNodeType, ValueType
from fangen.db.models import Request, RequestValue, Topic
from fangen.db.models.node import PlanNode

NodeData = dict[str, str | int | list | None]


def format_timestamp(time: int) -> str:
    return datetime.datetime.fromtimestamp(time / 1000, datetime.UTC).strftime(
        "%H:%M:%S"
    )


def parse_value(value: RequestValue) -> str | None:
    if value.value is None:
        return None
    if value.type is ValueType.CHECKBOX:
        return "Да" if parse_checkbox_value(value) else "Нет"
    if value.type is ValueType.IMAGE:
        image_value = parse_image_value(value)
        return build_cosplay2_image_link(
            event_id=value.request.topic.event_id,
            request_id=value.request_id,
            filename=image_value.filename,
        )
    if value.type is ValueType.FILE:
        file_value = parse_file_value(value)
        if file_value.filename:
            return build_cosplay2_file_link(
                event_id=value.request.topic.event_id,
                request_id=value.request_id,
                filename=file_value.filename,
            )
        return file_value.link
    if value.type is ValueType.DURATION:
        td = parse_duration_value(value)
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    return str(value.value)


def parse_event_node(event: PlanNode) -> dict:
    return {"info": event.title}


def parse_topic(topic: Topic) -> dict:
    return {"info": topic.title, "code": topic.card_code}


def parse_request(request: Request) -> dict:
    data: NodeData = {
        "info": request.voting_title,
        "title": request.voting_title,
        "code": request.topic.card_code if request.topic else None,
        "topic_title": request.topic.title if request.topic else None,
        "card": request.voting_number,
    }
    for value in request.values:
        value: RequestValue
        processed_value = parse_value(value)
        # If there are multiple values with same
        # key put them in a list
        existing_value = data.get(value.title)
        if existing_value and isinstance(existing_value, list):
            existing_value.append(processed_value)
            data[value.title] = existing_value
        elif existing_value:
            data[value.title] = [existing_value, processed_value]
        else:
            data[value.title] = processed_value
    return data


def get_node_data(node: PlanNode) -> NodeData:
    # Basic node data
    data: NodeData = {
        "uid": node.uid,
        "type": node.type,
        "title": node.title,
        "request_length": node.request_length,
        "time_start": node.time_start,
        "time_end": node.time_end,
        "time": format_timestamp(node.time_start) if node.time_start else None,
    }
    if node.type is PlanNodeType.EVENT:
        data.update(parse_event_node(node))
    if node.type is PlanNodeType.TOPIC:
        data.update(parse_topic(node.topic))
    if node.type is PlanNodeType.REQUEST:
        data.update(parse_request(node.request))
    return data
