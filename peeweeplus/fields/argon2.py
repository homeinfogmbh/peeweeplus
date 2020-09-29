"""Argon2-based password hashing."""

from argon2 import extract_parameters, PasswordHasher
from peewee import FieldAccessor

from peeweeplus.exceptions import PasswordTooShortError
from peeweeplus.fields.password import PasswordField
from peeweeplus.introspection import FieldType


__all__ = ['Argon2Hash', 'Argon2FieldAccessor', 'Argon2Field']


class Argon2Hash(str):
    """An Argon2 hash."""

    def __new__(cls, string, _):
        """Retuns a new Argon2Hash."""
        return super().__new__(cls, string)

    def __init__(self, _, hasher):
        """Sets the hasher."""
        super().__init__()
        self.hasher = hasher

    @classmethod
    def from_plaintext(cls, plaintext, hasher):
        """Creates an Argon2 hash from a plain text password."""
        return cls(hasher.hash(plaintext), hasher)

    @property
    def needs_rehash(self):
        """Determines whether the password needs a rehash."""
        return self.hasher.check_needs_rehash(self)

    @property
    def parameters(self):
        """Returns the Argon2 hash parameters."""
        return extract_parameters(self)

    def verify(self, passwd):
        """Validates the plain text password against this hash."""
        return self.hasher.verify(self, passwd)


class Argon2FieldAccessor(FieldAccessor):  # pylint: disable=R0903
    """Accessor class for Argon2Field."""

    def __set__(self, instance, value):
        """Sets the password hash."""
        if value is not None:
            if not isinstance(value, Argon2Hash):
                length = len(value)

                # If value is a plain text password, hash it.
                if length < self.field.min_pw_len:
                    raise PasswordTooShortError(length, self.field.min_pw_len)

                value = Argon2Hash.from_plaintext(value, self.field.hasher)

        super().__set__(instance, value)


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
