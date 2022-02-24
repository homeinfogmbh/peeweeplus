"""Database introspection."""

from __future__ import annotations
from re import fullmatch
from typing import NamedTuple

from peewee import Field


__all__ = ['FieldType']


FIELD_TYPE = '^([a-z]+)\\((\\d*)\\)$'
FIELD_TYPE_QUERY = (
    'SELECT COLUMN_TYPE FROM information_schema.COLUMNS WHERE '
    'TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s'
)


class FieldType(NamedTuple):
    """Represents a database field type."""

    type: str
    size: int

    @classmethod
    def from_field(cls, field: Field) -> FieldType:
        """Returns the field type."""
        database = field.model._meta.database
        values = (
            database.database,
            field.model._meta.table_name,
            field.column_name
        )
        cursor = database.execute_sql(FIELD_TYPE_QUERY, values)
        result, *_ = cursor.fetchone()
        match = fullmatch(FIELD_TYPE, result)
        type_, size = match.groups()
        size = int(size) if size else None
        return cls(type_, size)
