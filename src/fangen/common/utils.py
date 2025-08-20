import re


def build_cosplay2_image_link(event_id: int, request_id: int, filename: str) -> str:
    return f"https://cosplay2.ru/uploads/{event_id}/{request_id}/{filename}.jpg"


def build_cosplay2_file_link(event_id: int, request_id: int, filename: str) -> str:
    return f"https://cosplay2.ru/uploads/{event_id}/{request_id}/{filename}"


def format_template(template: str, data: dict, dictionary: dict) -> str:
    variable_pattern = r"\{(.*?)\}"

    def replace_match(match: re.Match[str]) -> str | None:
        keys_str = match.group(1)
        keys = keys_str.split("|")

        value = None
        for key in keys:
            for internal_key, possible_keys in dictionary.items():
                if key in possible_keys:
                    key = internal_key  # noqa: PLW2901
            value = data.get(key)

        return str(value) if value else None

    return re.sub(variable_pattern, replace_match, template)
