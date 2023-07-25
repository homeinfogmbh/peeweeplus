"""Integer fields."""

from peewee import IntegerField, SmallIntegerField


__all__ = [
    "SmallUnsignedIntegerField",
    "UnsignedIntegerField",
    "UnsignedBigIntegerField",
]


class SmallUnsignedIntegerField(SmallIntegerField):
    """Small unsigned integer field."""

    field_type = "SMALLINT UNSIGNED"


class UnsignedIntegerField(IntegerField):
    """Unsigned integer field."""

    field_type = "INT UNSIGNED"


class UnsignedBigIntegerField(IntegerField):
    """Unsigned big integer field."""

    field_type = "BIGINT UNSIGNED"
