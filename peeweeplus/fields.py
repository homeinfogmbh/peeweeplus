"""Additional field definitions."""

from datetime import datetime
from ipaddress import IPv4Address

from argon2 import PasswordHasher
from peewee import BigIntegerField, CharField, FixedCharField

from peeweeplus.converters import parse_float
from peeweeplus.introspection import FieldType
from peeweeplus.passwd import Argon2FieldAccessor, Argon2Hash


__all__ = [
    'EnumField',
    'PasswordField',
    'Argon2Field',
    'IPv4AddressField',
    'BooleanCharField',
    'IntegerCharField',
    'DecimalCharField',
    'DateTimeCharField',
    'DateCharField']


class EnumField(CharField):
    """CharField-based enumeration field."""

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
            return None

        return value.value

    def python_value(self, value):
        """Returns the respective enumeration."""
        if value is None:
            return None

        return self.enum(value)


class PasswordField(FixedCharField):    # pylint: disable=R0903
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

    def db_value(self, value):  # pylint: disable=R0201
        """Returns the string value."""
        return str(value)

    @property
    def actual_size(self):  # pylint: disable=R0201
        """Returns the actual field size."""
        return FieldType.from_field(self).size

    @property
    def size_changed(self):
        """Determines whether the size has changed."""
        return self.max_length != self.actual_size


class IPv4AddressField(BigIntegerField):
    """Field to store IPv4 addresses."""

    def db_value(self, value):  # pylint: disable=R0201
        """Returns the IPv4 address's interger value or None."""
        if value is None:
            return None

        return int(value)

    def python_value(self, value):  # pylint: disable=R0201
        """Returns the IPv4 address object or None."""
        if value is None:
            return None

        return IPv4Address(value)


class BooleanCharField(CharField):
    """Stores boolean values as text."""

    def __init__(self, *args, true='J', false='N', **kwargs):
        """Invokes super init and stores true and false values."""
        super().__init__(*args, **kwargs)
        self.true = true
        self.false = false

    def db_value(self, value):
        """Returns the database value."""
        if value is None:
            return None if self.null else ''

        return self.true if value else self.false

    def py_value(self, value):
        """Returns the python value."""
        if not value:
            return None

        if value == self.true:
            return True

        if value == self.false:
            return False

        raise ValueError(f'Invalid value for BooleanTextField: "{value}".')


class IntegerCharField(CharField):
    """Integers stored as strings."""

    def db_value(self, value):
        """Returns a string value for the database."""
        if value is None:
            return None if self.null else ''

        return str(value)

    def py_value(self, value):  # pylint: disable=R0201
        """Returns the stored string as integer."""
        return int(value) if value else None


class DecimalCharField(CharField):
    """Decimal values stored as strings."""

    def db_value(self, value):
        """Converts the value to a string using the first separator."""
        if value is None:
            return None if self.null else ''

        return str(value)

    def py_value(self, value):  # pylint: disable=R0201
        """Returns a float from the database string."""
        return parse_float(value) if value else None


class DateTimeCharField(CharField):
    """A CharField that stores datetime values."""

    def __init__(self, *args, format='%c', **kwargs):   # pylint: disable=W0622
        """Invokes super init and sets the format."""
        super().__init__(*args, **kwargs)
        self.format = format

    def db_value(self, value):
        """Returns a string for the database."""
        if value is None:
            return None if self.null else ''

        return value.strftime(self.format)

    def py_value(self, value):
        """Returns a datetime object for python."""
        return datetime.strptime(value, self.format) if value else None


class DateCharField(DateTimeCharField):
    """A CharField that stores date values."""

    def py_value(self, value):
        """Returns a datetime object for python."""
        if not value:
            return None

        return datetime.strptime(value, self.format).date()
