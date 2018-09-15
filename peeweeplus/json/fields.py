"""Miscellaneous stuff."""

from collections import namedtuple
from functools import lru_cache

from peewee import ForeignKeyField

from functoolsplus import coerce
from strflib import camel_case

from peeweeplus.exceptions import NullError


__all__ = ['contains', 'json_fields', 'FieldConverter']


JSONField = namedtuple('JSONField', ('key', 'attribute', 'field'))


def contains(iterable, *items):
    """Determines whether the field is contained within the iterable."""

    if not iterable:
        return False

    return any(item in iterable for item in items)


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


class FieldConverter(tuple):
    """Maps conversion functions to field classes in preserved order."""

    def __new__(cls, *items):
        """Creates a new tuple."""
        return super().__new__(cls, items)

    @lru_cache()
    def __call__(self, field, value, check_null=False):
        """Converts the respective value to the field."""
        if value is None:
            if check_null and not field.null:
                raise NullError()

            return None

        for classes, function in self:
            if isinstance(field, classes):
                return function(value)

        return value
