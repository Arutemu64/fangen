import re
from functools import cache

from rich import print

# Separator used when a single field holds several values. Rendering them as a
# joined string keeps cells readable instead of leaking Python's list repr
# (e.g. "['a', 'b']") into Excel output and filled templates.
MULTI_VALUE_SEPARATOR = "; "

# Marker that separates the field key(s) from an optional value transform
# inside a template placeholder, e.g. "{Персонаж:s/,.*//}". Only the
# substitution operator ("s/.../.../") is recognised, so a bare colon inside a
# Cosplay2 field title stays part of the key.
TRANSFORM_MARKER = ":s/"

# A well-formed "s/pattern/replacement/flags" transform splits into exactly
# these four parts once the leading "s" is dropped: ["", pattern, repl, flags].
_TRANSFORM_PARTS = 4

# Transforms that fail to compile / apply are reported once each; templates are
# reused for every request, so without this guard a bad pattern would spam the
# console with one warning per row.
_warned_transforms: set[str] = set()


def build_cosplay2_image_link(event_id: int, request_id: int, filename: str) -> str:
    return f"https://cosplay2.ru/uploads/{event_id}/{request_id}/{filename}.jpg"


def build_cosplay2_file_link(event_id: int, request_id: int, filename: str) -> str:
    return f"https://cosplay2.ru/uploads/{event_id}/{request_id}/{filename}"


def _warn_bad_transform(transform: str) -> None:
    if transform in _warned_transforms:
        return
    _warned_transforms.add(transform)
    print(
        f"[!] Не удалось применить преобразование шаблона «:{transform}»; "
        "значение поля оставлено без изменений."
    )


@cache
def _compile_transform(transform: str) -> tuple[re.Pattern[str], str, int] | None:
    """Parse an "s/pattern/replacement/flags" transform into applyable parts.

    Returns a (compiled_pattern, replacement, count) triple, or None when the
    transform is malformed. Cached so each unique transform is compiled once
    per run rather than once per request.
    """
    # `transform` still carries the leading "s"; drop it and split the rest on
    # slashes that are not backslash-escaped. A well-formed "s/a/b/flags" yields
    # exactly ["", "a", "b", "flags"].
    parts = re.split(r"(?<!\\)/", transform[1:])
    if len(parts) != _TRANSFORM_PARTS or parts[0] != "":
        _warn_bad_transform(transform)
        return None
    _, pattern, replacement, flags = parts
    # Restore escaped delimiters to literal slashes inside both halves.
    pattern = pattern.replace(r"\/", "/")
    replacement = replacement.replace(r"\/", "/")
    # "i" -> case-insensitive; "g" -> replace every match (default: first only).
    re_flags = re.IGNORECASE if "i" in flags else 0
    count = 0 if "g" in flags else 1
    try:
        compiled = re.compile(pattern, re_flags)
    except re.error:
        _warn_bad_transform(transform)
        return None
    return compiled, replacement, count


def format_template(template: str, data: dict) -> str:
    variable_pattern = r"\{(.*?)\}"

    def replace_match(match: re.Match[str]) -> str:
        content = match.group(1)

        # Split off an optional "s/.../.../" transform. The key part keeps any
        # other colons, so field titles like "Ссылка: VK" are unaffected.
        marker = content.find(TRANSFORM_MARKER)
        if marker != -1:
            keys_part = content[:marker]
            transform = content[marker + 1 :]  # keep the leading "s"
        else:
            keys_part = content
            transform = None

        keys = keys_part.split("|")
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
            rendered = MULTI_VALUE_SEPARATOR.join(parts)
        else:
            rendered = str(value) if value else ""

        if transform:
            compiled = _compile_transform(transform)
            if compiled is not None:
                pattern, replacement, count = compiled
                try:
                    rendered = pattern.sub(replacement, rendered, count=count)
                except re.error:
                    # e.g. an invalid backreference in the replacement string.
                    # Fall back to the untransformed value instead of raising.
                    _warn_bad_transform(transform)

        return rendered

    return re.sub(variable_pattern, replace_match, template)
