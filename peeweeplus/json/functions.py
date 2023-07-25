"""JSON-related functions."""

from re import sub


__all__ = ["camel_case"]


def camel_case(string: str) -> str:
    """Converts a snake_case string to camelCase."""

    return sub(r"_(\w)", lambda match: match.group(1).upper(), string)
