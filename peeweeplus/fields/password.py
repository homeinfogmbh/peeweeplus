"""Password field."""

from peewee import FixedCharField


__all__ = ["PasswordField"]


class PasswordField(FixedCharField):
    """Common base class for password
    fields to identify them as such.
    """
