"""Additional field definitions."""

from ipaddress import IPv4Address

from argon2 import PasswordHasher
from peewee import CharField, FixedCharField, ForeignKeyField, BigIntegerField

from peeweeplus.converters import parse_float
from peeweeplus.introspection import FieldType
from peeweeplus.passwd import Argon2Hash, Argon2FieldAccessor


__all__ = [
    'EnumField',
    'CascadingFKField',
    'PasswordField',
    'Argon2Field',
    'IPv4AddressField',
    'BooleanCharField',
    'IntegerCharField',
    'DecimalCharField']


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


class CascadingFKField(ForeignKeyField):    # pylint: disable=R0903
    """A ForeignKeyField with default cascading."""

    def __init__(self, *args, on_delete='CASCADE', on_update='CASCADE',
                 **kwargs):     # pylint: disable=W0235
        """Delegates to ForeignKeyField.__init__."""
        super().__init__(
            *args, on_delete=on_delete, on_update=on_update, **kwargs)


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

    def __init__(self, max_length, true='J', false='N', **kwargs):
        """Invokes super init and stores true and false values."""
        super().__init__(max_length, **kwargs)
        self.true = true
        self.false = false

    def db_value(self, value):
        """Returns the database value."""
        if value is None:
            if self.null:
                return None

            return ''

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
            if self.null:
                return None

            return ''

        return str(value)

    def py_value(self, value):  # pylint: disable=R0201
        """Returns the stored string as integer."""
        if not value:
            return None

        return int(value)


class DecimalCharField(CharField):
    """Decimal values stored as strings."""

    def db_value(self, value):
        """Converts the value to a string using the first separator."""
        if value is None:
            if self.null:
                return None

            return ''

        return str(value)

    def py_value(self, value):  # pylint: disable=R0201
        """Returns a float from the database string."""
        if not value:
            return None

        return parse_float(value)
