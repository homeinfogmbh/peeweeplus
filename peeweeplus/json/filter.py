"""Serialization filter."""

from typing import NamedTuple

from peewee import AutoField
from peewee import ForeignKeyField
from peeweeplus.fields import PasswordField
from peeweeplus.json.fields import contains


__all__ = ['FieldsFilter']


class FieldsFilter(NamedTuple):
    """Field filtering settings."""

    skip: frozenset
    only: frozenset
    fk_fields: bool
    autofields: bool
    passwords: bool

    @classmethod
    def for_deserialization(cls, skip=None, only=None, fk_fields=False,
                            passwords=True):
        """Creates the filter from the respective keyword arguments."""
        skip = frozenset(skip) if skip else frozenset()
        only = frozenset(only) if only else frozenset()
        return cls(skip, only, fk_fields, False, passwords)

    @classmethod
    def for_serialization(cls, skip=None, only=None, fk_fields=True,
                          autofields=True):
        """Creates the filter from the respective keyword arguments."""
        skip = frozenset(skip) if skip else frozenset()
        only = frozenset(only) if only else frozenset()
        return cls(skip, only, fk_fields, autofields, False)

    def filter(self, fields):
        """Applies this filter to the respective fields."""
        for key, attribute, field in fields:
            if contains(self.skip, key, attribute, default=False):
                continue

            if not contains(self.only, key, attribute, default=True):
                continue

            if isinstance(field, PasswordField) and not self.passwords:
                continue

            if isinstance(field, ForeignKeyField) and not self.fk_fields:
                continue

            if isinstance(field, AutoField) and not self.autofields:
                continue

            yield (key, attribute, field)
