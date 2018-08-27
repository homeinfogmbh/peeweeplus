"""Miscellaneous stuff."""

from functools import lru_cache

from peewee import ForeignKeyField

from peeweeplus.exceptions import NullError


__all__ = ['contained', 'json_fields', 'FieldConverter']


def contained(key, iterable):
    """Determines whether the field is contained within the iterable."""

    if not iterable:
        return False

    return key in iterable


def _json_fields(model):
    """Yields the JSON fields of the respective model."""

    fields = model._meta.fields     # pylint: disable=W0212
    field_keys = {}
    field_attributes = {}

    for attribute, field in fields.items():
        if not attribute.startswith('_'):
            if isinstance(field, ForeignKeyField):
                # Compensate for fast FK access.
                field_attributes[field] = attribute + '_id'

            field_keys[field] = field.column_name

    for model in reversed(model.__mro__):   # pylint: disable=R1704
        # Create map of custom keys for fields.
        json_keys = model.__dict__.get('JSON_KEYS')

        if not json_keys:
            continue

        custom_keys = {field: key for key, field in json_keys.items()}
        # Override column names with custom set field keys.
        field_keys.update(custom_keys)

    for field, key in field_keys.items():
        attribute = field_attributes.get(field, field.name)
        yield (field, attribute, key)


@lru_cache()
def json_fields(model):
    """Returns a cached frozen set of JSON
    fields of the respective model.
    """

    return frozenset(_json_fields(model))


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
