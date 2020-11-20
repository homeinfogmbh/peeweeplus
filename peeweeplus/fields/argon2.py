"""Argon2-based password hashing."""

from __future__ import annotations
from typing import Union

from argon2 import Parameters, PasswordHasher, extract_parameters
from peewee import Field, FieldAccessor, Model

from peeweeplus.exceptions import PasswordTooShortError
from peeweeplus.fields.password import PasswordField
from peeweeplus.introspection import FieldType


__all__ = ['Argon2Field']


class Argon2Hash(str):
    """An Argon2 hash."""

    def __new__(cls, string: str, _):
        """Retuns a new Argon2Hash."""
        return super().__new__(cls, string)

    def __init__(self, _, field: Field):
        """Sets the hasher."""
        super().__init__()
        self._field = field
        self._instance = None

    @classmethod
    def from_plaintext(cls, plaintext: str, field: Field) -> Argon2Hash:
        """Creates an Argon2 hash from a plain text password."""
        return cls(field.hasher.hash(plaintext), field)

    @property
    def needs_rehash(self) -> bool:
        """Determines whether the password needs a rehash."""
        return self._field.hasher.check_needs_rehash(self)

    @property
    def parameters(self) -> Parameters:
        """Returns the Argon2 hash parameters."""
        return extract_parameters(self)

    @property
    def _accessor(self) -> Argon2FieldAccessor:
        """Returns the accessor."""
        return self._field.accessor_class(
            self._field.model, self._field, self._field.name)

    def _set(self, passwd: str):
        """Updates the hash."""
        if self._instance is None:
            raise TypeError('Instance not set.')

        self._accessor.__set__(self._instance, passwd)

    def verify(self, passwd: str) -> bool:
        """Validates the plain text password against this hash."""
        return self._field.hasher.verify(self, passwd)

    def rehash(self, passwd: str, *, force: bool = False) -> bool:
        """Performs a rehash."""
        if force or self.needs_rehash:
            self._set(passwd)
            return True

        return False


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

                value = Argon2Hash.from_plaintext(value, self.field)

            if len(value) != self.field.actual_size:
                raise ValueError('Hash length does not match char field size.')

            value._instance = instance

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

    @property
    def actual_size(self) -> int:
        """Returns the actual field size."""
        return FieldType.from_field(self).size
