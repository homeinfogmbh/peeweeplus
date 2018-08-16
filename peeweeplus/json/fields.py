"""Miscellaneous stuff."""

from peeweeplus.exceptions import NullError


__all__ = ['json_fields', 'FieldConverter']


def json_fields(model):
    """Yields the JSON fields of the respective model."""

    fields_map = {}

    for model in reversed(model.__mro__):   # pylint: disable=R1704
        # Map model fields' column names to the model's fields.
        fields = model._meta.fields     # pylint: disable=W0212
        field_keys = {field: field.column_name for field in fields.items()}
        # Create map of custom keys for fields.
        custom_keys = model.__dict__.get('JSON_KEYS', {})
        custom_keys = {field: key for key, field in custom_keys.items()}
        # Override column names with custom set field keys.
        field_keys.update(custom_keys)
        # Update total fields map.
        fields_map.update(field_keys)

    for field, key in fields_map.items():
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
