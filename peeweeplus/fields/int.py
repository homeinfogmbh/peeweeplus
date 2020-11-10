"""Integer fields."""

from peewee import IntegerField


__all__ = ['UnsignedIntegerField', 'UnsignedBigIntegerField']


class UnsignedIntegerField(IntegerField):
    """Unsigned integer field."""

    field_type = 'INT UNSIGNED'


class UnsignedBigIntegerField(IntegerField):
    """Unsigned big integer field."""

    field_type = 'BIGINT UNSIGNED'
