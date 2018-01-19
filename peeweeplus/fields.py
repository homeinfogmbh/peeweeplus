"""Additional field definitions."""

from contextlib import suppress

from peewee import CharField

__all__ = ['InvalidEnumerationValue', 'EnumField']


class InvalidEnumerationValue(ValueError):
    """Indicates that an invalid enumeration value has been specified."""

    def __init__(self, value):
        super().__init__('Invalid enum value: "{}".'.format(value))


class EnumField(CharField):
    """CharField-based enumeration field."""

    def __init__(self, enum, *args, max_length=None, null=None, **kwargs):
        """Initializes the enumeration field with the possible values.

        :values: The respective enumeration.
        :max_length: Ignored.
        :null: Ignored.
        """
        super().__init__(*args, max_length=max_length, null=null, **kwargs)
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
            raise TypeError('Cannot set max_length to non-None value.')

    @property
    def null(self):
        """Determines nullability by enum values."""
        return any(value is None for value in self.values)

    @null.setter
    def null(self, null):
        """Mockup to comply with super class' __init__."""
        if null is not None:
            raise TypeError('Cannot set null to non-None value.')

    def db_value(self, value):
        """Coerce enumeration value for database."""
        with suppress(AttributeError):
            value = value.value

        if value in self.values:
            return value

        raise InvalidEnumerationValue(value)

    def python_value(self, value):
        """Coerce enumeration value for python."""
        for enum in self.enum:
            if enum.value == value:
                return enum

        raise InvalidEnumerationValue(value)
