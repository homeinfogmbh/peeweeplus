"""Argon2-based password hashing."""

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from peewee import FieldAccessor

from peeweeplus.exceptions import PasswordTooShortError

__all__ = ['PASSWORD_HASHER', 'Argon2FieldAccessor']


PASSWORD_HASHER = PasswordHasher()
_MIN_PW_LEN = 8


def _is_hash(value, hasher=PASSWORD_HASHER):
    """Determines whether value is a valid Argon2 hash for hasher."""

    try:
        return hasher.verify(value, '')
    except VerifyMismatchError:
        return True
    except VerificationError:
        return False


class _Argon2Hash(str):
    """An Argon2 hash."""

    def __new__(cls, value, hasher):
        """Override str constructor."""
        string = str.__new__(cls, value)

        if not _is_hash(string, hasher):
            raise ValueError(string)

        return string

    def __init__(self, _, hasher):
        """Sets the hasher."""
        super().__init__()
        self._hasher = hasher

    def verify(self, passwd):
        """Validates the plain text password against this hash."""
        return self._hasher.verify(self, passwd)


class Argon2FieldAccessor(FieldAccessor):
    """Accessor class for Argon2Field."""

    def __get__(self, instance, instance_type=None):
        """Returns an Argon2 hash."""
        value = super().__get__(instance, instance_type=instance_type)

        if instance is not None:
            if value is None:
                return None
            elif isinstance(value, _Argon2Hash):
                return value

            return _Argon2Hash(value, self.field.hasher)

        return value

    def __set__(self, instance, value):
        """Sets the password hash or hashes the password."""
        if value is not None:
            try:
                value = _Argon2Hash(value, self.field.hasher)
            except ValueError:
                if len(value) < _MIN_PW_LEN:
                    raise PasswordTooShortError(len(value), _MIN_PW_LEN)

                value = self.field.hasher.hash(value)
                value = _Argon2Hash(value, self.field.hasher)

        super().__set__(instance, value)
