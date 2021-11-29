"""Miscellaneous stuff."""

from contextlib import suppress
from functools import lru_cache
from typing import Iterable, Iterator, NamedTuple, Set

from peewee import Field, ForeignKeyField, ModelBase

from peeweeplus.exceptions import NullError
from peeweeplus.json.functions import camel_case


__all__ = ['JSON_FIELDS', 'contains', 'get_json_fields', 'FieldConverter']


JSON_FIELDS = {}
CACHE_LIMIT = 1024 * 1024


class JSONField(NamedTuple):
    """JSON field information tuple."""

    key: str
    attribute: str
    field: Field


def contains(iterable: Iterable, key: str, attribute: str, *,
             default: bool = False) -> bool:
    """Determines whether the field is contained within the iterable."""

    if iterable:
        return key in iterable or attribute in iterable

    return default


def _get_json_fields(model: ModelBase) -> Iterator[JSONField]:
    """Yields the JSON fields of the respective model."""

    fields = model._meta.fields     # pylint: disable=W0212

    for attribute, field in fields.items():
        if attribute.startswith('_'):
            continue

        if isinstance(field, ForeignKeyField):
            if attribute.endswith('_id') and attribute + '_id' not in fields:
                continue

        yield JSONField(camel_case(field.column_name), field.name, field)


def get_json_fields(model: ModelBase) -> Set[JSONField]:
    """Returns the JSON fields of the respective model
    and caches it in the JSON_FIELDS dict.
    """

    with suppress(KeyError):
        return JSON_FIELDS[model]

    JSON_FIELDS[model] = fields = frozenset(_get_json_fields(model))
    return fields


class FieldConverter(dict):
    """Maps conversion functions to field classes."""

    def __call__(self, field: Field, value: object,
                 check_null: bool = False) -> object:
        """Converts the respective value to the field."""
        @lru_cache(maxsize=CACHE_LIMIT, typed=True)
        def cached(field: Field, value: object, check_null: bool):
            """Caches the result."""
            if value is None:
                if check_null and not field.null:
                    raise NullError()

                return None

            for parent in type(field).__mro__:
                try:
                    function = self[parent]
                except KeyError:
                    continue

                with suppress(TypeError):
                    return function(value)

                return function(value, field)

            return value

        return cached(field, value, check_null)
