"""Argon2-based password hashing."""

from argon2 import extract_parameters


__all__ = ['Argon2Hash']


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
