"""Additional field definitions."""

from ipaddress import IPv4Address

from argon2 import PasswordHasher
from peewee import CharField, FixedCharField, ForeignKeyField, BigIntegerField

from peeweeplus.enum import EnumFieldAccessor
from peeweeplus.exceptions import InvalidEnumerationValue
from peeweeplus.functions import field_type
from peeweeplus.passwd import Argon2Hash, Argon2FieldAccessor


__all__ = ['EnumField', 'CascadingFKField', 'Argon2Field', 'IPv4AddressField']


class EnumField(CharField):
    """CharField-based enumeration field."""

    accessor_class = EnumFieldAccessor

    def __init__(self, enum, *args, **kwargs):
        """Initializes the enumeration field with the enumeration enum.
        The keyword max_length is not supported.
        """
        super().__init__(*args, max_length=None, **kwargs)
        self.enum = enum

    @property
    def max_length(self):
        """Derives the required field size from the enumeration values."""
        return max(len(value.value) for value in self.enum)

    @max_length.setter
    def max_length(self, max_length):   # pylint: disable=R0201
        """Mockup to comply with super class' __init__."""
        if max_length is not None:
            raise AttributeError('Cannot set max_length property.')

    def db_value(self, value):
        """Coerce enumeration value for database."""
        if value is None:
            if self.null:
                return None

            raise InvalidEnumerationValue(value, self.enum)

        return value.value


class CascadingFKField(ForeignKeyField):
    """A ForeignKeyField with default cascading."""

    def __init__(self, *args, on_delete='CASCADE', on_update='CASCADE',
                 **kwargs):
        """Delegates to ForeignKeyField.__init__."""
        super().__init__(
            *args, on_delete=on_delete, on_update=on_update, **kwargs)


class PasswordField(FixedCharField):
    """Common base class for password
    fields to identify them as such.
    """


class Argon2Field(PasswordField):   # pylint: disable=R0901
    """An Argon2 password field."""

    accessor_class = Argon2FieldAccessor

    def __init__(self, hasher=PasswordHasher(), min_pw_len=8, **kwargs):
        """Initializes the char field, defaulting
        max_length to the respective hash length.
        """
        super().__init__(max_length=len(hasher.hash('')), **kwargs)
        self.hasher = hasher
        self.min_pw_len = min_pw_len

    def python_value(self, value):
        """Returns an Argon2 hash."""
        if value is None:
            return None

        return Argon2Hash(value, self.hasher)


class IPv4AddressField(BigIntegerField):
    """Field to store IPv4 addresses."""

    def db_value(self, value):
        """Returns the IPv4 address's interger value or None."""
        if value is None:
            return None

        return int(value)

    def python_value(self, value):
        """Returns the IPv4 address object or None."""
        if value is None:
            return None

        return IPv4Address(value)

    @property
    def actual_size(self):
        """Returns the actual field size."""
        _, size = field_type(self)
        return size
