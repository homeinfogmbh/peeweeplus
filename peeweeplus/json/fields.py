"""Miscellaneous stuff."""

from functools import lru_cache
from typing import NamedTuple

from peewee import Field, ForeignKeyField

from functoolsplus import coerce
from strflib import camel_case

from peeweeplus.exceptions import NullError


__all__ = ['contains', 'json_fields', 'FieldConverter']


class JSONField(NamedTuple):
    """JSON field information tuple."""

    key: str
    attribute: str
    field: Field


def contains(iterable, key, attribute, *, default=False):
    """Determines whether the field is contained within the iterable."""

    if iterable:
        return key in iterable or attribute in iterable

    return default


@lru_cache()
@coerce(frozenset)
def json_fields(model):
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


class FieldConverter(dict):
    """Maps conversion functions to field classes in preserved order."""

    def __call__(self, field, value, check_null=False):
        """Converts the respective value to the field."""
        if value is None:
            if check_null and not field.null:
                raise NullError()

            return None

        function, wants_field = self.get_params(type(field))

        if wants_field:
            return function(value, field)

        return function(value)

    def get_params(self, field_class):
        """Returns the appropriate function for the given field class."""
        for parent in field_class.__mro__:
            try:
                entry = self[parent]
            except KeyError:
                continue

            try:
                function, wants_field = entry
            except ValueError:
                return (entry, False)

            return (function, wants_field)

        return (lambda value: value, False)
