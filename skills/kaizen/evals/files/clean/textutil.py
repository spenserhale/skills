"""Small text helpers."""


def truncate(text, limit):
    """Cut text to limit characters, ending with an ellipsis when cut."""
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def initials(name):
    """Return the uppercase initials of a name."""
    return "".join(part[0].upper() for part in name.split())
