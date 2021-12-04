"""Specialized character-based fields."""

from datetime import date, datetime
from typing import Iterable, Optional, Union

from peewee import CharField, FieldAccessor

from peeweeplus.converters import parse_float


__all__ = [
    'BooleanCharField',
    'IntegerCharField',
    'DecimalCharField',
    'DateTimeCharField',
    'DateCharField',
    'RestrictedCharField'
]


class EmptyableCharField(CharField):
    """A Char field that might be empty."""

    def __init__(self, *args, null: bool = False, default: str = None,
                 **kwargs):
        """Updates the default value."""
        if default is None and not null:
            default = ''

        super().__init__(*args, null=null, default=default, **kwargs)

    def db_value(self, value: str) -> str:
        """Converts the value to a string using the first separator."""
        if value is None:
            return None if self.null else ''

        return str(value)


class BooleanCharField(EmptyableCharField):
    """Stores boolean values as text."""

    def __init__(self, *args, true: str = 'J', false: str = 'N', **kwargs):
        """Invokes super init and stores true and false values."""
        super().__init__(*args, **kwargs)
        self.true = true
        self.false = false

    def db_value(self, value: bool) -> str:
        """Returns the database value."""
        if value is None:
            return None if self.null else ''

        return self.true if value else self.false

    def python_value(self, value: str) -> bool:
        """Returns the python value."""
        if not value:
            return None

        if value == self.true:
            return True

        if value == self.false:
            return False

        raise ValueError(f'Invalid value for BooleanTextField: "{value}".')


class IntegerCharField(EmptyableCharField):
    """Integers stored as strings."""

    def python_value(self, value: str) -> int:  # pylint: disable=R0201
        """Returns the stored string as integer."""
        return int(value) if value else None


class DecimalCharField(EmptyableCharField):
    """Decimal values stored as strings."""

    def python_value(self, value: str) -> float:    # pylint: disable=R0201
        """Returns a float from the database string."""
        return parse_float(value) if value else None


class DateTimeCharField(EmptyableCharField):
    """A CharField that stores datetime values."""

    def __init__(self, *args, format: str = '%c', **kwargs):
        """Invokes super init and sets the format."""
        super().__init__(*args, **kwargs)
        self.format = format

    def db_value(self, value: Union[date, datetime]) -> str:
        """Returns a string for the database."""
        if value is not None:
            return None if self.null else ''

        return value.strftime(self.format)

    def python_value(self, value: str) -> datetime:
        """Returns a datetime object for python."""
        return datetime.strptime(value, self.format) if value else None


class DateCharField(DateTimeCharField):     # pylint: disable=R0901
    """A CharField that stores date values."""

    def python_value(self, value: str) -> date:
        """Returns a datetime object for python."""
        if not value:
            return None

        return datetime.strptime(value, self.format).date()


class RestrictedCharFieldAccessor(FieldAccessor):   # pylint: disable=R0903
    """Accessor class for HTML data."""

    def __get__(self, instance: type, instance_type: Optional[type] = None):
        value = super().__get__(instance, instance_type=instance_type)

        if instance is None:
            return value

        if value is None:
            return None

        return self.field.check(value)


class RestrictedCharField(CharField):
    """CharField with restricted character set."""

    def __init__(self, allowed_chars: Iterable[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_chars = allowed_chars

    def check(self, text: str) -> str:
        """Checks the text against the allowed chars."""
        if all(char in self.allowed_chars for char in text):
            return text

        raise ValueError('Text contains invalid characters.')

    accessor_class = RestrictedCharFieldAccessor
