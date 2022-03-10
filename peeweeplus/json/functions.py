"""JSON-related functions."""

from typing import Iterator


__all__ = ['camel_case']


def _camel_case(string: str, *, first_caps: bool = False) -> Iterator[str]:
    """Yields characters converted to camelCase."""

    underscore = False

    for index, char in enumerate(string):
        if char == '_':
            underscore = True
        elif underscore:
            underscore = False
            yield char.upper()
        elif index == 0 and first_caps:
            yield char.upper()
        else:
            yield char


def camel_case(string: str, *, first_caps: bool = False) -> str:
    """Converts a snake_case string to camelCase."""

    string = string.strip('_')
    return ''.join(_camel_case(string, first_caps=first_caps))
