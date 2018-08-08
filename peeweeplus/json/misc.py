"""Miscellaneous stuff."""

from peewee import AutoField, ForeignKeyField

from peeweeplus.exceptions import NullError, MissingKeyError, InvalidKeys
from peeweeplus.fields import PasswordField


__all__ = [
    'json_fields',
    'json_key',
    'deserialization_filter',
    'serialization_filter',
    'FieldMap']


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


def deserialization_filter(
        model, dictionary, patch, allow=(), deny=(), strict=True):
    """Filters the respective fields, yielding
        (<attribute>, <field>, <key>, <value>)
    tuples.
    """

    invalid_keys = set()
    allowed_keys = set()

    for attribute, field in json_fields(model, autofields=False):
        key = json_key(field)

        if allow and key not in allow:
            invalid_keys.add(key)
            continue

        if deny and key in deny:
            invalid_keys.add(key)
            continue

        allowed_keys.add(key)

        try:
            value = dictionary[key]
        except KeyError:
            if not patch and field.default is None and not field.null:
                raise MissingKeyError(model, attribute, field, key)

            continue

        yield (attribute, field, key, value)

    if strict:
        if invalid_keys:
            raise InvalidKeys(invalid_keys)

        unprocessed = {key for key in dictionary if key not in allowed_keys}

        if unprocessed:
            raise InvalidKeys(unprocessed)


def serialization_filter(
        record, allow=(), deny=(), null=False, autofields=True):
    """Yields the respective dictionary items in the form of
    (<key>, <field>, <value>).
    """

    for attribute, field in json_fields(type(record), autofields=autofields):
        key = json_key(field)

        if allow and key not in allow:
            continue

        if deny and key in deny:
            continue

        value = getattr(record, attribute)

        if value is not None or null:
            yield (key, field, value)


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
