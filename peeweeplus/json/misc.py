"""Miscellaneous stuff."""

from peewee import AutoField, ForeignKeyField

from peeweeplus.exceptions import NullError
from peeweeplus.fields import PasswordField


__all__ = ['json_fields', 'json_key', 'FieldMap']


def json_fields(model, autofields=True):
    """Yields JSON name, attribute name and field
    instance for each field  of the model.
    """

    for attribute, field in model._meta.fields.items():  # pylint:disable=W0212
        # Skip hidden fields iff they are not explicitely given a JSON key.
        if attribute.startswith('_') and not hasattr(field, 'json_key'):
            continue

        # Forbid FK fields, since it is not generally clear whether
        # to cascade the FK model or just yield the FK ID.
        # Override JSONModel.to_dict() if needed.
        # Also forbid password fields because of obvious data leakage.
        if isinstance(field, (ForeignKeyField, PasswordField)):
            continue

        # We generally do not want AutoFields (PK fields) on deserialization.
        if not autofields and isinstance(field, AutoField):
            continue

        yield (attribute, field)


def json_key(field):
    """Returns the key for JSON serialization."""

    try:
        return field.json_key
    except AttributeError:
        return field.column_name


class FieldMap(tuple):
    """Maps conversion functions to field classes in preserved order."""

    def __new__(cls, *items):
        """Creates a new tuple."""
        return super().__new__(cls, items)

    def convert(self, field, value, check_null=False):
        """Converts the respective value to the field."""
        if value is None:
            if check_null and not field.null:
                raise NullError()

            return None

        for classes, function in self:
            if isinstance(field, classes):
                return function(value)

        return value
