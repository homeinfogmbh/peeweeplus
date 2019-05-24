"""Database introspection."""

from re import compile  # pylint: disable=W0622
from typing import NamedTuple


__all__ = ['FieldType']


FIELD_TYPE = compile('^([a-z]+)\\((\\d*)\\)$')
FIELD_TYPE_QUERY = (
    "SELECT COLUMN_TYPE FROM information_schema.COLUMNS WHERE "
    "TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s")


class FieldType(NamedTuple):
    """Represents the type of a fields."""

    type: str
    size: int

    @classmethod
    def from_field(cls, field):
        """Returns the field type."""
        database = field.model._meta.database   # pylint: disable=W0212
        values = (
            database.database,
            field.model._meta.table_name,   # pylint: disable=W0212
            field.column_name)
        cursor = database.execute_sql(FIELD_TYPE_QUERY, values)
        result, *_ = cursor.fetchone()
        match = FIELD_TYPE.fullmatch(result)
        type_, size = match.groups()
        size = int(size) if size else None
        return cls(type_, size)
