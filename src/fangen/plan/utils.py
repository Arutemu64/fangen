import datetime
import json
import re
from contextlib import suppress
from json import JSONDecodeError
from pathlib import Path

from fangen.cosplay2.models.plan import PlanNodeType
from fangen.cosplay2.models.value import ValueType
from fangen.db.models import RequestValue
from fangen.db.models.node import PlanNode


NodeContext = dict[str, str | int | list | None]


def generate_request_link(request_id: int, event_name: str) -> str:
    return f"https://{event_name}.cosplay2.ru/orgs/requests/request/{request_id}"


def format_timestamp(time: int) -> str:
    return datetime.datetime.fromtimestamp(time / 1000, datetime.UTC).strftime(
        "%H:%M:%S"
    )


def preprocess_request_value(value: RequestValue) -> str:
    if value.type is ValueType.CHECKBOX:
        if value.value == "YES":
            return "Да"
        else:
            return "Нет"
    if value.type is ValueType.IMAGE:
        with suppress(JSONDecodeError):
            image_info = json.loads(value.value)
            event_id = value.request.topic.event_id
            request_id = value.request_id
            filename = image_info["filename"]
            return f"https://cosplay2.ru/uploads/{event_id}/{request_id}/{filename}.jpg"
    if value.type is ValueType.FILE:
        with suppress(JSONDecodeError):
            file_info = json.loads(value.value)
            if filename := file_info.get("filename"):
                return f"Файл: {filename}"
            if link := file_info.get("link"):
                return f"Ссылка: {link}"
    return str(value.value)


def parse_event_node(event: PlanNode) -> dict:
    return {
        "info": event.title,
        "time": format_timestamp(event.time_start) if event.time_start else None,
    }


def parse_topic_node(topic: PlanNode) -> dict:
    return {"info": topic.title, "code": topic.topic.card_code}


def parse_request_node(request: PlanNode, event_name: str) -> dict:
    data: NodeContext = {
        "info": f"{request.request.voting_title}\n({generate_request_link(request.request_id, event_name)})",
        "title": request.request.voting_title,
        "code": request.topic.card_code if request.topic else None,
        "card": request.request.voting_number,
        "time": format_timestamp(request.time_start) if request.time_start else None,
    }
    for value in request.request.values:
        value: RequestValue
        processed_value = preprocess_request_value(value)
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


def get_node_context(
    node: PlanNode, request_number: int, event_name: str
) -> NodeContext:
    data: NodeContext = {
        "uid": node.uid,
        "type": node.type,
        "title": node.title,
        "request_length": node.request_length,
        "time_start": node.time_start,
        "time_end": node.time_end,
    }
    if node.type is PlanNodeType.EVENT:
        data.update(parse_event_node(node))
    if node.type is PlanNodeType.TOPIC:
        data.update(parse_topic_node(node))
    if node.type is PlanNodeType.REQUEST:
        data.update({"n": request_number})
        data.update(parse_request_node(node, event_name))
    return data


def format_header(header: str, context: NodeContext, dict_path: Path) -> str:
    variable_pattern = r"\{(.*?)\}"

    with open(dict_path, "r", encoding="utf-8") as f:
        dictionary = json.load(f)

    def replace_match(match: re.Match[str]) -> str | None:
        keys_str = match.group(1)
        keys = keys_str.split("|")

        value = None
        for key in keys:
            for internal_key, possible_keys in dictionary.items():
                if key in possible_keys:
                    key = internal_key
            value = context.get(key)

        return str(value) if value else None

    return re.sub(variable_pattern, replace_match, header)
