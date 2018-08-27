"""Data type parsers."""

from base64 import b64decode
from datetime import datetime, date, time

from timelib import strpdatetime, strpdate, strptime    # pylint: disable=E0401


__all__ = [
    'parse_bool',
    'parse_datetime',
    'parse_date',
    'parse_time',
    'parse_blob',
    'get_fk_value']


def parse_bool(value):
    """Parses a boolean value."""

    if isinstance(value, (bool, int)):
        return bool(value)

    raise ValueError(value)


def parse_datetime(value):
    """Parses a datetime value."""

    if isinstance(value, datetime):
        return value

    return strpdatetime(value)


def parse_date(value):
    """Parses a date value."""

    if isinstance(value, date):
        return value

    return strpdate(value)


def parse_time(value):
    """Parses a time value."""

    if isinstance(value, time):
        return value

    return strptime(value)


def parse_blob(value):
    """Parses a blob value."""

    if isinstance(value, bytes):
        return value

    return b64decode(value)


def get_fk_value(value):
    """Returns the foreign key value."""

    try:
        return value._pk    # pylint: disable=W0212
    except AttributeError:
        return int(value)
