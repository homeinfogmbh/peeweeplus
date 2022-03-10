"""Data type parsers."""

from base64 import b64decode
from datetime import datetime, date, time
from enum import Enum
from typing import Union

from peewee import CharField

from peeweeplus.fields.enum import EnumField


__all__ = [
    'parse_bool',
    'parse_char_field',
    'parse_datetime',
    'parse_date',
    'parse_time',
    'parse_blob',
    'parse_enum'
]


def parse_bool(value: Union[bool, int]) -> bool:
    """Parses a boolean value."""

    if isinstance(value, (bool, int)):
        return bool(value)

    raise ValueError(value)


def parse_char_field(value: str, field: CharField) -> str:
    """Parses a string for a char field."""

    if field.max_length is None:
        return value

    if (size := len(value)) > field.max_length:
        raise ValueError(f'String is too long: {size} > {field.max_length}')

    return value


def parse_datetime(value: Union[datetime, str]) -> datetime:
    """Parses a datetime value."""

    if isinstance(value, datetime):
        return value

    return datetime.fromisoformat(value)


def parse_date(value: Union[date, str]) -> date:
    """Parses a date value."""

    if isinstance(value, date):
        return value

    return date.fromisoformat(value)


def parse_time(value: Union[time, str]) -> time:
    """Parses a time value."""

    if isinstance(value, time):
        return value

    return time.fromisoformat(value)


def parse_blob(value: Union[bytes, str]) -> bytes:
    """Parses a blob value."""

    if isinstance(value, bytes):
        return value

    return b64decode(value)


def parse_enum(value: Union[Enum, str], field: EnumField) -> Enum:
    """Parses an enumeration value."""

    if isinstance(value, field.enum):
        return value

    return field.enum(value)
