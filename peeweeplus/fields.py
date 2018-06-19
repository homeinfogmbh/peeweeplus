"""Additional field definitions."""

from contextlib import suppress
from uuid import uuid4

from peewee import CharField, FixedCharField, ForeignKeyField

__all__ = [
    'InvalidEnumerationValue',
    'EnumField',
    'CascadingFKField',
    'TokenField']


class InvalidEnumerationValue(ValueError):
    """Indicates that an invalid enumeration value has been specified."""

    def __init__(self, value):
        super().__init__('Invalid enum value: "{}".'.format(value))


class EnumField(CharField):
    """CharField-based enumeration field."""

    def __init__(self, enum, *args, **kwargs):
        """Initializes the enumeration field with the enumeration enum.
        The keyword max_length is not supported.
        """
        super().__init__(*args, max_length=None, **kwargs)
        self.enum = enum

    @property
    def values(self):
        """Yields the enumeration values."""
        for enum in self.enum:
            yield enum.value

    @property
    def max_length(self):
        """Derives the required field size from the enumeration values."""
        return max(len(value) for value in self.values if value is not None)

    @max_length.setter
    def max_length(self, max_length):
        """Mockup to comply with super class' __init__."""
        if max_length is not None:
            raise AttributeError('Cannot set max_length property.')

    @property
    def null(self):
        """Determines nullability by enum values."""
        return self.__null or any(value is None for value in self.values)

    @null.setter
    def null(self, null):
        """Mockup to comply with super class' __init__."""
        self.__null = null

    def db_value(self, value):
        """Coerce enumeration value for database."""
        with suppress(AttributeError):
            value = value.value

        if value in self.values or value is None and self.null:
            return value

        raise InvalidEnumerationValue(value)

    def python_value(self, value):
        """Coerce enumeration value for python."""
        for enum in self.enum:
            if enum.value == value:
                return enum

        if value is None and self.null:
            return value

        raise InvalidEnumerationValue(value)


class CascadingFKField(ForeignKeyField):
    """A ForeignKeyField with default cascading."""

    def __init__(self, *args, on_delete='CASCADE', on_update='CASCADE',
                 **kwargs):
        """Delegates to ForeignKeyField.__init__."""
        super().__init__(
            *args, on_delete=on_delete, on_update=on_update, **kwargs)


class TokenField(FixedCharField):
    """A UUID4 token field."""

    def __init__(self, default=lambda: str(uuid4()), **kwargs):
        """Initializes the char field."""
        super().__init__(max_length=64, default=default, **kwargs)
