"""Argon2-based password hashing."""

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from peewee import FieldAccessor

from peeweeplus.exceptions import PasswordTooShortError

__all__ = ['PASSWORD_HASHER', 'Argon2Hash', 'Argon2FieldAccessor']


PASSWORD_HASHER = PasswordHasher()
MIN_LEN = 8


def is_hash(value, hasher=PASSWORD_HASHER):
    """Determines whether value is a valid Argon2 hash for hasher."""

    try:
        return hasher.verify(value, '')
    except VerifyMismatchError:
        return True
    except VerificationError:
        return False


class Argon2Hash(str):
    """An Argon2 hash."""

    def __new__(cls, value, hasher):
        """Override str constructor."""
        string = str.__new__(cls, value)

        if not is_hash(string, hasher):
            raise ValueError(string)

        return string

    def __init__(self, _, hasher):
        """Sets the hasher."""
        super().__init__()
        self.hasher = hasher

    def verify(self, passwd):
        """Validates the plain text password against this hash."""
        return self.hasher.verify(self, passwd)


class Argon2FieldAccessor(FieldAccessor):
    """Accessor class for Argon2Field."""

    def __set__(self, instance, value):
        """Sets the password hash or hashes the password."""
        if not isinstance(value, str):
            raise TypeError(type(value))

        if not is_hash(value, hasher=self.field.hasher):
            if len(value) < MIN_LEN:
                raise PasswordTooShortError(MIN_LEN, len(value))

            value = self.field.hasher.hash(value)

        super().__set__(instance, value)
