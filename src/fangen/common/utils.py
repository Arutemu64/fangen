import re

# Separator used when a single field holds several values. Rendering them as a
# joined string keeps cells readable instead of leaking Python's list repr
# (e.g. "['a', 'b']") into Excel output and filled templates.
MULTI_VALUE_SEPARATOR = "; "


def build_cosplay2_image_link(event_id: int, request_id: int, filename: str) -> str:
    return f"https://cosplay2.ru/uploads/{event_id}/{request_id}/{filename}.jpg"


def build_cosplay2_file_link(event_id: int, request_id: int, filename: str) -> str:
    return f"https://cosplay2.ru/uploads/{event_id}/{request_id}/{filename}"


def format_template(template: str, data: dict) -> str:
    variable_pattern = r"\{(.*?)\}"

    def replace_match(match: re.Match[str]) -> str:
        keys = match.group(1).split("|")

        value = None
        for key in keys:
            value = data.get(key)
            if value:
                # Use the first key that resolves to a non-empty value
                break

        if isinstance(value, list):
            # Several values under one field title: join them into a flat
            # string rather than emitting Python's list repr.
            parts = [
                str(item) for item in value if item is not None and str(item) != ""
            ]
            return MULTI_VALUE_SEPARATOR.join(parts)
        return str(value) if value else ""

    return re.sub(variable_pattern, replace_match, template)
