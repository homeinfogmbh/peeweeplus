"""Argon2-based password hashing."""

from collections import namedtuple
from contextlib import suppress

from argon2 import extract_parameters
from argon2.exceptions import VerifyMismatchError
from peewee import FieldAccessor

from peeweeplus.exceptions import PasswordTooShortError


__all__ = ['Argon2Hash', 'Argon2FieldAccessor']



class Argon2Hash(namedtuple('Argon2Hash', ('hash', 'hasher'))):
    """An Argon2 hash."""

    def __str__(self):
        """Returns the hash string."""
        return self.hash

    @classmethod
    def from_string(cls, string, hasher):
        """Returns an Argon2 hash from the respective string and hasher."""
        with suppress(VerifyMismatchError):
            hasher.verify(string, '')

        return cls(string, hasher)

    @property
    def needs_rehash(self):
        """Determines whether the password needs a rehash."""
        return self.hasher.check_needs_rehash(self.hash)

    @property
    def parameters(self):
        """Returns the Argon2 hash parameters."""
        return extract_parameters(self.hash)

    def verify(self, passwd):
        """Validates the plain text password against this hash."""
        return self.hasher.verify(self.hash, passwd)


class Argon2FieldAccessor(FieldAccessor):   # pylint: disable=R0903
    """Accessor class for Argon2Field."""

    def __set__(self, instance, value):
        """Sets the password hash."""
        if value is not None:
            if not isinstance(value, Argon2Hash):
                length = len(value)

                # If value is a plain text password, hash it.
                if length < self.field.min_pw_len:
                    raise PasswordTooShortError(length, self.field.min_pw_len)

                value = self.field.hasher.hash(value)

        super().__set__(instance, value)
