"""Miscellaneous stuff."""

from peeweeplus.exceptions import NullError


__all__ = ['json_fields', 'FieldConverter']


def json_fields(model):
    """Yields the JSON fields of the respective model."""

    fields = {}

    for model in reversed(model.__mro__):   # pylint: disable=R1704
        fields.update(model.__dict__.get('JSON_FIELDS', {}))

    return fields


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
