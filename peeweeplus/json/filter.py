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

    @classmethod
    def for_deserialization(cls, **kwargs):
        """Creates the filter from the respective keyword arguments."""
        skip = kwargs.get('skip')
        skip = frozenset(skip) if skip else frozenset()
        only = kwargs.get('only')
        only = frozenset(only) if only else frozenset()
        fk_fields = kwargs.get('fk_fields', False)
        return cls(skip, only, fk_fields, False)

    @classmethod
    def for_serialization(cls, **kwargs):
        """Creates the filter from the respective keyword arguments."""
        skip = kwargs.get('skip')
        skip = frozenset(skip) if skip else frozenset()
        only = kwargs.get('only')
        only = frozenset(only) if only else frozenset()
        fk_fields = kwargs.get('fk_fields', True)
        autofields = kwargs.get('autofields', True)
        return cls(skip, only, fk_fields, autofields)

    def filter(self, fields):
        """Applies this filter to the respective fields."""
        for key, attribute, field in fields:
            if contains(self.skip, key, attribute, default=False):
                continue
            elif not contains(self.only, key, attribute, default=True):
                continue
            elif isinstance(field, PasswordField):
                continue
            elif not self.fk_fields and isinstance(field, ForeignKeyField):
                continue
            elif not self.autofields and isinstance(field, AutoField):
                continue

            yield (key, attribute, field)
