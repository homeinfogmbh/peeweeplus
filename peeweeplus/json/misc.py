"""Miscellaneous stuff."""

from contextlib import suppress

from peewee import Field, AutoField, ForeignKeyField

from peeweeplus.exceptions import NullError
from peeweeplus.fields import PasswordField


__all__ = ['json_fields', 'json_key', 'FieldList', 'FieldMap']


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
        # Also forbit password fields because of obvious data leakage.
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


class FieldList:
    """A list of DB columns, attributes or fields."""

    def __init__(self, items):
        """Splits into a list of strings and fields."""
        self.strings = set()
        self.fields = []
        self.field_types = []

        for item in items:
            if isinstance(item, Field):
                self.fields.append(item.__class__)
                continue

            with suppress(TypeError):
                if issubclass(item, Field):
                    self.field_types.append(item)
                    continue

            self.strings.add(item)

    def __contains__(self, item):
        """Determines whether the list contains either
        the DB column's name, attribute or field.
        """
        column_name, attribute, field = item

        if column_name in self.strings or attribute in self.strings:
            return True

        if isinstance(field, tuple(self.fields)):
            return True

        return issubclass(field, tuple(self.field_types))


class FieldMap(tuple):
    """Maps conversion functions to field classes in preserved order."""

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
