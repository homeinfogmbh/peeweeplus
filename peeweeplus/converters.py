"""Converter functions."""

from timelib import strpdatetime


__all__ = ['dec2dom', 'dec2dict', 'dec2orm', 'date2orm', 'datetime2orm']


def dec2dom(value):
    """Converts a decimal into a DOM compliant value."""

    if value is None:
        return None

    return str(value)


def dec2dict(value):
    """Converts a decimal-like string into a JSON-compliant value."""

    if value is None:
        return None

    return float(value)


def dec2orm(value):
    """Converts a decimal into an ORM compliant value."""

    return dec2dict(value)


def date2orm(value):
    """Converts a date object to a ORM compliant value."""

    if value is None:
        return None

    return value.date()


def datetime2orm(value):
    """Converts a datetime object to a ORM comliant value."""

    if value is None:
        return None

    return strpdatetime(value.isoformat())
