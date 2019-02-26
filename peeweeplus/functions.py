"""Functions an hacks."""

from re import compile  # pylint: disable=W0622


__all__ = ['field_type']


FIELD_TYPE = compile('^([a-z]+)\\((\\d*)\\)$')
FIELD_TYPE_QUERY = (
    "SELECT COLUMN_TYPE FROM information_schema.COLUMNS WHERE "
    "TABLE_SCHEMA = ? AND TABLE_NAME = ? AND COLUMN_NAME = ?")


def field_type(field):
    """Returns the field type."""

    database = field.model._meta.database   # pylint: disable=W0212
    values = (
        database.database,
        field.model._meta.table_name,   # pylint: disable=W0212
        field.column_name)
    cursor = database.execute_sql(FIELD_TYPE_QUERY, values)
    result, *_ = cursor.fetchone()
    match = FIELD_TYPE.fullmatch(result)
    type_, length = match.groups()
    length = int(length) if length else None
    return (type_, length)
