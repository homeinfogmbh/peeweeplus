"""Converter functions."""

from timelib import strpdatetime


__all__ = [
    'dec2dom',
    'dec2dict',
    'dec2orm',
    'date2orm',
    'datetime2orm',
    'parse_float']


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


def parse_float(string):
    """Parses a float from a comma or dot (or both) containing string."""

    if ',' in string and '.' in string:
        if string.index(',') > string.index('.'):
            string = string.replace('.', '')
            string = string.replace(',', '.')
        else:
            string = string.replace(',', '')

        return float(string)

    if ',' in string:
        if sum(char == ',' for char in string) > 1:
            string = string.replace(',', '')
        else:
            string = string.replace(',', '.')

        return float(string)

    if sum(char == '.' for char in string) > 1:
        string = string.replace('.', '')

    return float(string)
