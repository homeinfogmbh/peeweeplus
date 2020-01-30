"""Integer fields."""

from peewee import IntegerField


__all__ = ['UnsignedIntegerField']


class UnsignedIntegerField(IntegerField):
    """Unsigned integer field."""

    field_type = 'INT UNSIGNED'
