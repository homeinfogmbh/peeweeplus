"""Miscellaneous stuff."""

from collections import namedtuple
from functools import lru_cache

from functoolsplus import returning
from peeweeplus.exceptions import NullError


__all__ = ['contained', 'json_fields', 'get_pk_value', 'FieldConverter']


JSONField = namedtuple('JSONField', ('key', 'field'))


def contained(key, iterable):
    """Determines whether the field is contained within the iterable."""

    if not iterable:
        return False

    return key in iterable


@lru_cache()
@returning(frozenset)
def json_fields(model):
    """Yields the JSON fields of the respective model."""

    fields = model._meta.fields     # pylint: disable=W0212
    field_keys = {}

    for attribute, field in fields.items():
        if not attribute.startswith('_'):
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
        yield JSONField(key, field)


def get_pk_value(value):
    """Returns the respective primary key value."""

    try:
        return value._pk    # pylint: disable=W0212
    except AttributeError:
        return int(value)


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
