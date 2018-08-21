"""Miscellaneous stuff."""

from peeweeplus.exceptions import NullError


__all__ = ['contained', 'json_fields', 'FieldConverter']


def contained(field, iterable):
    """Determines wether the field is contained within the iterable."""

    if not iterable:
        return False

    return (
        field.name in iterable or field.json_key in iterable or
        field in iterable or type(field) in iterable)   # pylint: disable=C0123


def json_fields(model):
    """Yields the JSON fields of the respective model."""

    field_keys = {
        field: None for attribute, field in model._meta.fields.items()
        if not attribute.startswith('_')}

    for model in reversed(model.__mro__):
        # Create map of custom keys for fields.
        json_keys = model.__dict__.get('JSON_KEYS')

        if not json_keys:
            continue

        custom_keys = {field: key for key, field in json_keys.items()}
        # Override column names with custom set field keys.
        field_keys.update(custom_keys)

    for field, key in field_keys.items():
        field.json_key = key
        yield field


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
