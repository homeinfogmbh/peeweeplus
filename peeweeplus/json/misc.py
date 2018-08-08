"""Miscellaneous stuff."""

from peewee import AutoField, ForeignKeyField

from peeweeplus.exceptions import NullError
from peeweeplus.fields import PasswordField


__all__ = ['json_fields', 'json_key', 'FieldConverter']


def json_fields(model, fk_fields=True, autofields=True):
    """Yields JSON name, attribute name and field
    instance for each field  of the model.
    """

    for attribute, field in model._meta.fields.items():  # pylint:disable=W0212
        # Skip hidden fields iff they are not explicitely given a JSON key.
        if attribute.startswith('_') and not hasattr(field, 'json_key'):
            continue

        # Forbid password fields because of obvious data leakage.
        if isinstance(field, PasswordField):
            continue

        if not fk_fields and isinstance(field, ForeignKeyField):
            continue

        if not autofields and isinstance(field, AutoField):
            continue

        yield (attribute, field)


def json_key(field):
    """Returns the key for JSON serialization."""

    try:
        return field.json_key
    except AttributeError:
        return field.column_name


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
