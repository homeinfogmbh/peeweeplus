"""Enumeration fields."""

from enum import Enum, EnumMeta

from peewee import CharField


__all__ = ['EnumField']


class EnumField(CharField):
    """CharField-based enumeration field."""

    def __init__(self, enum: EnumMeta, *args, **kwargs):
        """Initializes the enumeration field with the enumeration enum.
        The keyword max_length is not supported.
        """
        super().__init__(*args, max_length=None, **kwargs)
        self.enum = enum

    @property
    def max_length(self) -> int:
        """Derives the required field size from the enumeration values."""
        return max(len(value.value) for value in self.enum)

    @max_length.setter
    def max_length(self, max_length: int):   # pylint: disable=R0201
        """Mockup to comply with super class' __init__."""
        if max_length is not None:
            raise AttributeError('Cannot set max_length property.')

    def db_value(self, value: Enum) -> str:
        """Coerce enumeration value for database."""
        if value is None:
            return None

        return value.value

    def python_value(self, value: str) -> Enum:
        """Returns the respective enumeration."""
        if value is None:
            return None

        return self.enum(value)
