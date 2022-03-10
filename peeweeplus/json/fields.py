"""Miscellaneous stuff."""

from contextlib import suppress
from functools import lru_cache
from typing import Any, Iterable, Iterator, NamedTuple, Type

from peewee import Field, ForeignKeyField, Model

from peeweeplus.exceptions import NullError


__all__ = [
    'JSON_FIELDS',
    'JSONField',
    'FieldConverter',
    'contains',
    'get_json_fields',
]


JSON_FIELDS = {}
CACHE_LIMIT = 1024 * 1024


class JSONField(NamedTuple):
    """JSON field information tuple."""

    key: str
    attribute: str
    field: Field


class FieldConverter(dict):
    """Maps conversion functions to field classes."""

    def __call__(
            self,
            field: Field,
            value: Any,
            check_null: bool = False
    ) -> Any:
        """Converts the respective value to the field."""
        @lru_cache(maxsize=CACHE_LIMIT, typed=True)
        def _convert_field_value(
                field: Field,
                value: Any,
                check_null: bool
        ) -> Any:
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

        return _convert_field_value(field, value, check_null)


def contains(
        iterable: Iterable,
        key: str,
        attribute: str,
        *,
        default: bool = False
) -> bool:
    """Determines whether the field is contained within the iterable."""

    if iterable:
        return key in iterable or attribute in iterable

    return default


def get_json_fields(model: Type[Model]) -> frozenset[JSONField]:
    """Returns the JSON fields of the respective model
    and caches it in the JSON_FIELDS dict.
    """

    with suppress(KeyError):
        return JSON_FIELDS[model]

    JSON_FIELDS[model] = fields = frozenset(_get_json_fields(model))
    return fields


def _get_json_fields(model: Type[Model]) -> Iterator[JSONField]:
    """Yields the JSON fields of the respective model."""

    fields = model._meta.fields     # pylint: disable=W0212

    try:
        key_formatter = model.__key_formatter__
    except AttributeError:
        key_formatter = None

    for attribute, field in fields.items():
        if attribute.startswith('_'):
            continue

        if isinstance(field, ForeignKeyField):
            if attribute.endswith('_id') and attribute + '_id' not in fields:
                continue

        if key_formatter is not None:
            key = key_formatter(field.column_name)
        else:
            key = field.column_name

        yield JSONField(key, field.name, field)
