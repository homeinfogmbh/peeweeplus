"""Additional field definitions."""

from contextlib import suppress
from uuid import uuid4, UUID

from peewee import CharField, FixedCharField, ForeignKeyField

from peeweeplus.exceptions import InvalidEnumerationValue
from peeweeplus.passwd import HASH_SIZE, Argon2Hash, Argon2FieldAccessor

__all__ = ['EnumField', 'CascadingFKField', 'UUID4Field']


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

        raise InvalidEnumerationValue(value, self.enum)

    def python_value(self, value):
        """Coerce enumeration value for python."""
        for enum in self.enum:
            if enum.value == value:
                return enum

        if value is None and self.null:
            return value

        raise InvalidEnumerationValue(value, self.enum)


class CascadingFKField(ForeignKeyField):
    """A ForeignKeyField with default cascading."""

    def __init__(self, *args, on_delete='CASCADE', on_update='CASCADE',
                 **kwargs):
        """Delegates to ForeignKeyField.__init__."""
        super().__init__(
            *args, on_delete=on_delete, on_update=on_update, **kwargs)


class UUID4Field(FixedCharField):
    """A UUID4 token field."""

    def __init__(self, max_length=32, default=uuid4, **kwargs):
        """Initializes the char field."""
        super().__init__(max_length=max_length, default=default, **kwargs)

    def db_value(self, value):
        """Returns the hexadecimal string representation of the UUID."""
        if value is None:
            return None

        try:
            return value.hex
        except AttributeError:
            return UUID(value).hex

    def python_value(self, value):
        """Returns a UUID object or None."""
        if value is None:
            return None
        elif isinstance(value, UUID):
            return value

        return UUID(value)


class Argon2Field(FixedCharField):
    """An Argon2 password field."""

    accessor_class = Argon2FieldAccessor

    def __init__(self, max_length=HASH_SIZE, **kwargs):
        """Initializes the char field."""
        super().__init__(max_length=max_length, **kwargs)

    def db_value(self, value):
        """Returns the password hash as a string."""
        if value is None:
            return None

        return str(value)

    def python_value(self, value):
        """Returns a string-like Argon2Hash object."""
        if value is None:
            return None

        return Argon2Hash(value)
