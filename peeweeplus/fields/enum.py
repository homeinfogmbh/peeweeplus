"""Enumeration fields."""

from enum import Enum
from typing import Optional, Type

from peewee import CharField


__all__ = ["EnumField"]


class EnumField(CharField):
    """CharField-based enumeration field."""

    def __init__(self, enum: Type[Enum], use_name: bool = False, **kwargs):
        """Initializes the enumeration field with the enumeration enum.
        The keyword max_length is not supported.
        If use_name is True, store the enum's name instead of its value.
        """
        super().__init__(max_length=None, **kwargs)
        self.enum = enum
        self.use_name = use_name

    @property
    def max_length(self) -> int:
        """Derives the required field size from the enumeration values."""
        return max(
            len(value.name if self.use_name else value.value) for value in self.enum
        )

    @max_length.setter
    def max_length(self, max_length: int):
        """Mockup to comply with super class' __init__."""
        if max_length is not None:
            raise AttributeError("Cannot set max_length property.")

    def db_value(self, value: Enum) -> Optional[str]:
        """Coerce enumeration value for database."""
        if value is None:
            return None

        return value.name if self.use_name else value.value

    def python_value(self, value: str) -> Optional[Enum]:
        """Returns the respective enumeration."""
        if value is None:
            return None

        return self.enum[value] if self.use_name else self.enum(value)
