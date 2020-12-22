"""Argon2-based password hashing."""

from __future__ import annotations
from logging import getLogger
from typing import Union

from argon2 import Parameters, PasswordHasher, extract_parameters
from peewee import FieldAccessor, Model

from peeweeplus.exceptions import PasswordTooShortError
from peeweeplus.fields.password import PasswordField
from peeweeplus.introspection import FieldType


__all__ = ['Argon2Field']


LOGGER = getLogger('Argon2Field')


class Argon2Hash(str):
    """An Argon2 hash."""

    def __new__(cls, string: str, *_):
        """Retuns a new Argon2Hash."""
        return super().__new__(cls, string)

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


class Argon2FieldAccessor(FieldAccessor):  # pylint: disable=R0903
    """Accessor class for Argon2Field."""

    def __set__(self, instance: Model, value: Union[str, Argon2Hash]):
        """Sets the password hash."""
        if value is not None:
            if not isinstance(value, Argon2Hash):
                length = len(value)

                # If value is a plain text password, hash it.
                if length < self.field.min_pw_len:
                    raise PasswordTooShortError(length, self.field.min_pw_len)

                value = Argon2Hash.create(value, self.field.hasher)

            if len(value) != self.field.actual_size:
                raise ValueError('Hash length does not match char field size.')

        super().__set__(instance, value)


class Argon2Field(PasswordField):   # pylint: disable=R0901
    """An Argon2 password field."""

    accessor_class = Argon2FieldAccessor

    def __init__(self, hasher: PasswordHasher = PasswordHasher(),
                 min_pw_len: int = 8, **kwargs):
        """Initializes the char field, defaulting
        max_length to the respective hash length.
        """
        super().__init__(max_length=len(hasher.hash('')), **kwargs)
        self.hasher = hasher
        self.min_pw_len = min_pw_len
        self.hooks = set()

    def _generate_default(self) -> Argon2Hash:
        """Generates a default password."""
        plaintext = self._default()

        if not isinstance(plaintext, str):
            raise ValueError('{self._default} did not generate a str.')

        if len(plaintext) < self.min_pw_len:
            raise PasswordTooShortError(len(plaintext), self.min_pw_len)

        while True:
            try:
                callback = self.hooks.pop()
            except KeyError:
                break

            callback(plaintext)

        return Argon2Hash.create(plaintext, self.hasher)

    @property
    def default(self):
        """Returns the default."""
        if self._default is None:
            return None

        return self._generate_default   # Return callable (method).

    @default.setter
    def default(self, default):
        """Sets the default value."""
        if default is not None and not callable(default):
            LOGGER.warning('Static default passwords are a bad idea!')

        self._default = default

    @property
    def actual_size(self) -> int:
        """Returns the actual field size."""
        return FieldType.from_field(self).size

    def python_value(self, value: str) -> Argon2Hash:
        """Returns an Argon2 hash."""
        if value is None:
            return None

        return Argon2Hash(value, self)

    def db_value(self, value: Argon2Hash) -> str:
        """Returns the string value."""
        if value is None:
            return None

        return str(value)
