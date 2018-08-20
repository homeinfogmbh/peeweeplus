"""Argon2-based password hashing."""

from argon2 import extract_parameters
from argon2.exceptions import VerificationError, VerifyMismatchError
from peewee import FieldAccessor

from peeweeplus.exceptions import PasswordTooShortError


__all__ = ['is_hash', 'Argon2Hash', 'Argon2FieldAccessor']


def is_hash(hasher, value):
    """Determines whether value is a valid Argon2 hash for hasher."""

    try:
        return hasher.verify(value, '')
    except VerifyMismatchError:
        return True
    except VerificationError:
        return False


class Argon2Hash(str):
    """An Argon2 hash."""

    def __new__(cls, hash_, _):
        """Override str constructor."""
        return super().__new__(cls, hash_)

    def __init__(self, hash_, hasher):
        """Sets the hasher."""
        super().__init__()

        if not is_hash(hasher, hash_):
            raise ValueError('Not an Argon2 hash.')

        self._hasher = hasher

    @property
    def needs_rehash(self):
        """Determines whether the password needs a rehash."""
        return self._hasher.check_needs_rehash(self)

    @property
    def parameters(self):
        """Returns the Argon2 hash parameters."""
        return extract_parameters(self)

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

            return Argon2Hash(value, self.field.hasher)

        return value

    def __set__(self, instance, value):
        """Sets the password hash."""
        if value is not None:
            if isinstance(value, Argon2Hash):
                value = str(value)
            else:
                # If value is a plain text password, hash it.
                if len(value) < self.field.min_pw_len:
                    raise PasswordTooShortError(
                        len(value), self.field.min_pw_len)

                value = self.field.hasher.hash(value)

        super().__set__(instance, value)
