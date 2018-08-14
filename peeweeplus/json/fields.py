"""Miscellaneous stuff."""

from collections import namedtuple

from peeweeplus.exceptions import NullError


__all__ = ['fields', 'json_fields', 'JSONOptions', 'FieldConverter']


JSONOptions = namedtuple('JSONOptions', ('key', 'serialize', 'deserialize'))


def fields(model):
    """Yields fields of the respective model."""

    return model._meta.fields.items()


def json_fields(model):
    """Yields JSON name, attribute name and field
    instance for each field  of the model.
    """

    # Check if model class itself has JSON_FIELDS defined.
    if 'JSON_FIELDS' not in model.__dict__:
        return

    for attribute, field in fields(model):
        try:
            options = model.JSON_FIELDS[attribute]
        except KeyError:
            continue

        yield (attribute, field, JSONOptions(options))


class FieldConverter(tuple):
    """Maps conversion functions to field classes in preserved order."""

    def __new__(cls, *items):
        """Creates a new tuple."""
        return super().__new__(cls, items)

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
