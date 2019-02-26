"""Hacks to be used with caution."""

from re import compile  # pylint: disable=W0622


__all__ = ['field_type']


FIELD_TYPE = compile('^([a-z]+)\\((\\d*)\\)$')
FIELD_TYPE_QUERY_TEMPLATE = (
    "SELECT COLUMN_TYPE FROM information_schema.COLUMNS WHERE "
    "TABLE_SCHEMA = '%s' AND TABLE_NAME = '%s' AND COLUMN_NAME = '%s'")


def field_type(field):
    """Returns the field type."""

    database = field.model._meta.database   # pylint: disable=W0212
    table_schema = database.database
    table_name = field.model._meta.table_name   # pylint: disable=W0212
    column_name = field.column_name
    query = FIELD_TYPE_QUERY_TEMPLATE.format(
        table_schema, table_name, column_name)
    cursor = database.execute_sql(query)
    result, *_ = cursor.fetchone()
    match = FIELD_TYPE.fullmatch(result)
    type_, length = match.groups()
    length = int(length) if length else None
    return (type_, length)
