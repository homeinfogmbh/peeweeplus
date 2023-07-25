"""Serialization filter."""

from __future__ import annotations
from typing import Iterable, Iterator, NamedTuple, Optional

from peewee import AutoField
from peewee import ForeignKeyField
from peeweeplus.fields import PasswordField
from peeweeplus.json.fields import JSONField, contains


__all__ = ["FieldsFilter"]


class FieldsFilter(NamedTuple):
    """Field filtering settings."""

    skip: frozenset[str]
    only: frozenset[str]
    fk_fields: bool
    autofields: bool
    passwords: bool

    @classmethod
    def for_deserialization(
        cls,
        skip: Optional[Iterable[str]] = None,
        only: Optional[Iterable[str]] = None,
        fk_fields: bool = False,
        passwords: bool = True,
    ) -> FieldsFilter:
        """Creates the filter from the respective keyword arguments."""
        skip = frozenset(skip) if skip else frozenset()
        only = frozenset(only) if only else frozenset()
        return cls(skip, only, fk_fields, False, passwords)

    @classmethod
    def for_serialization(
        cls,
        skip: Optional[Iterable[str]] = None,
        only: Optional[Iterable[str]] = None,
        fk_fields: bool = True,
        autofields: bool = True,
    ) -> FieldsFilter:
        """Creates the filter from the respective keyword arguments."""
        skip = frozenset(skip) if skip else frozenset()
        only = frozenset(only) if only else frozenset()
        return cls(skip, only, fk_fields, autofields, False)

    def filter(self, fields: Iterable[JSONField]) -> Iterator[JSONField]:
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

            yield JSONField(key, attribute, field)
