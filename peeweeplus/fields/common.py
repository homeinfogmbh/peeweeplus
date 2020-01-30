"""Common field types."""

from peewee import FixedCharField


class PasswordField(FixedCharField):    # pylint: disable=R0903
    """Common base class for password
    fields to identify them as such.
    """
