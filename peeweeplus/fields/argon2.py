"""Argon2-based password hashing."""

from __future__ import annotations
from logging import getLogger
from typing import Optional

from argon2 import Parameters, PasswordHasher, extract_parameters
from peewee import FieldAccessor, Model

from peeweeplus.exceptions import PasswordTooShort
from peeweeplus.fields.password import PasswordField
from peeweeplus.introspection import FieldType


__all__ = ["Argon2Field"]


LOGGER = getLogger("Argon2Field")


class Argon2Hash(str):
    """An Argon2 hash."""

    def __new__(cls, argon2hash: str, *_):
        """Returns a new Argon2Hash."""
        return super().__new__(cls, argon2hash)

    def __init__(self, _, hasher: PasswordHasher):
        """Sets the hasher."""
        super().__init__()
        self.hasher = hasher

    @classmethod
    def create(cls, plaintext: str, hasher: PasswordHasher) -> Argon2Hash:
        """Creates an Argon2 hash from a plain text password."""
        return cls(hasher.hash(plaintext), hasher)

    @property
    def needs_rehash(self) -> bool:
        """Determines whether the password needs a rehash."""
        return self.hasher.check_needs_rehash(self)

    @property
    def parameters(self) -> Parameters:
        """Returns the Argon2 hash parameters."""
        return extract_parameters(self)

    def verify(self, passwd: str) -> bool:
        """Validates the plain text password against this hash."""
        return self.hasher.verify(self, passwd)


class Argon2FieldAccessor(FieldAccessor):
    """Accessor class for Argon2Field."""

    def __set__(self, instance: Model, value: Optional[str]):
        """Sets the password hash."""
        if value is None:
            return super().__set__(instance, value)

        if not isinstance(value, Argon2Hash):
            # If value is a plain text password, hash it.
            if (length := len(value)) < self.field.min_pw_len:
                raise PasswordTooShort(length, self.field.min_pw_len)

            value = Argon2Hash.create(value, self.field.hasher)

        if len(value) != self.field.actual_size:
            raise ValueError("Hash length does not match char field size.")

        return super().__set__(instance, value)


class Argon2Field(PasswordField):
    """An Argon2 password field."""

    accessor_class = Argon2FieldAccessor

    def __init__(
        self,
        hasher: PasswordHasher = PasswordHasher(),
        min_pw_len: int = 8,
        default: type = None,
        **kwargs,
    ):
        """Initializes the char field, defaulting
        max_length to the respective hash length.
        """
        super().__init__(max_length=len(hasher.hash("")), **kwargs)
        self.hasher = hasher
        self.min_pw_len = min_pw_len

        if default is not None:
            LOGGER.warning("Default values are being ignored!")

    @property
    def actual_size(self) -> int:
        """Returns the actual field size."""
        return FieldType.from_field(self).size

    def python_value(self, value: str) -> Optional[Argon2Hash]:
        """Returns an Argon2 hash."""
        if value is None:
            return None

        return Argon2Hash(value, self.hasher)

    def db_value(self, value: Argon2Hash) -> Optional[str]:
        """Returns the string value."""
        if value is None:
            return None

        return str(value)
