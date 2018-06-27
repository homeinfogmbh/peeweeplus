"""Argon2-based password hashing."""

from argon2 import PasswordHasher
from peewee import FieldAccessor

__all__ = ['HASH_SIZE', 'Argon2Hash', 'Argon2FieldAccessor']


_PASSWORD_HASHER = PasswordHasher()
HASH_SIZE = len(_PASSWORD_HASHER.hash(''))


class Argon2Hash(str):
    """An Argon2 hash."""

    def verify(self, passwd):
        """Validates the plain text password against this hash."""
        return _PASSWORD_HASHER.verify(self, passwd)


class Argon2FieldAccessor(FieldAccessor):
    """Accessor class for Argon2Field."""

    def __set__(self, instance, value):
        """Sets the hashed password."""
        super().__set__(instance, Argon2Hash(_PASSWORD_HASHER.hash(value)))
