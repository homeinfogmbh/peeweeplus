"""Miscellaneous stuff."""

from contextlib import suppress
from functools import lru_cache
from typing import Generator, Iterable, NamedTuple

from peewee import Field, ForeignKeyField, ModelBase

from strflib import camel_case

from peeweeplus.exceptions import NullError


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


def _get_json_fields(model: ModelBase) -> Generator[JSONField, None, None]:
    """Yields the JSON fields of the respective model."""

    fields = model._meta.fields     # pylint: disable=W0212
    field_keys = {}
    field_attributes = {}

    for attribute, field in fields.items():
        if not attribute.startswith('_'):
            # Default JSON keys are column names in camelCase.
            field_keys[field] = camel_case(field.column_name)

            if isinstance(field, ForeignKeyField):
                id_attr = attribute + '_id'

                if hasattr(model, id_attr):
                    field_attributes[field] = id_attr

    for model in reversed(model.__mro__):   # pylint: disable=R1704
        # Create map of custom keys for fields.
        json_keys = model.__dict__.get('JSON_KEYS')

        if not json_keys:
            continue

        # Inverse key → field hashing to field → key hashing.
        # The reason we do this is because during model definition,
        # keys are not yet bound to the model and thus cannot be hashed yet.
        custom_keys = {field: key for key, field in json_keys.items()}
        # Override column names with custom set field keys.
        field_keys.update(custom_keys)

    for field, key in field_keys.items():
        attribute = field_attributes.get(field, field.name)
        yield JSONField(key, attribute, field)


def get_json_fields(model: ModelBase) -> frozenset:
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
