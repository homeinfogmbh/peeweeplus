"""JSON-related functions."""

from re import Match, subn
from typing import Iterator


__all__ = ['camel_case']


CAMEL_CASE_TO_SNAKE_CASE_GROUPS = r'(.?(?:[^a-z_]+(?=[A-Z_]|$)|[^A-Z_]+))'


def _snake_case_match(match: Match) -> str:
    """Conditionally Prefixes snake case matches."""

    group = match.group()
    prefix = bool(match.start() and not group.startswith('_'))
    return '_' * prefix + group.lower()


def snake_case(string: str) -> str:
    """Converts a camelCase string to snake_case."""

    return subn(CAMEL_CASE_TO_SNAKE_CASE_GROUPS, _snake_case_match, string)[0]


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
