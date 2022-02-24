"""Converter functions."""

from datetime import date, datetime
from typing import Any, Optional


__all__ = [
    'dec2dom',
    'dec2dict',
    'dec2orm',
    'date2orm',
    'datetime2orm',
    'parse_float'
]


def dec2dom(value: Any) -> Optional[str]:
    """Converts a decimal into a DOM compliant value."""

    if value is None:
        return None

    return str(value)


def dec2dict(value: Any) -> Optional[float]:
    """Converts a decimal-like string into a JSON-compliant value."""

    if value is None:
        return None

    return float(value)


dec2orm = dec2dict


def date2orm(value: Any) -> Optional[date]:
    """Converts a date object to a ORM compliant value."""

    if value is None:
        return None

    return value.date()


def datetime2orm(value: Any) -> Optional[datetime]:
    """Converts a datetime object to a ORM comliant value."""

    if value is None:
        return None

    return datetime.fromisoformat(value.isoformat())


def parse_float_with_comma_and_decimal(string: str) -> float:
    """Parses a float that contains a comma and a decimal point."""

    if string.index(',') < string.index('.'):
        return float(string.replace(',', ''))

    return float(string.replace('.', '').replace(',', '.'))


def parse_float_with_comma(string: str) -> float:
    """Parses a float that contains a comma."""

    if '.' in string:
        return parse_float_with_comma_and_decimal(string)

    if string.count(',') > 1:
        return float(string.replace(',', ''))

    return float(string.replace(',', '.'))


def parse_float(string: str) -> float:
    """Parses a float from a comma or dot (or both) containing string."""

    if ',' in string:
        return parse_float_with_comma(string)

    if string.count('.') > 1:
        return float(string.replace('.', ''))

    return float(string)
