"""Miscellaneous stuff."""

from collections import namedtuple

from peeweeplus.exceptions import NullError


__all__ = ['fields', 'json_fields', 'JSONOptions', 'FieldConverter']


class JSONOptions(namedtuple('JSONOptions', 'key serialize deserialize')):
    """Represents the configuration options of a JSON field."""

    __slots__ = ()

    @classmethod
    def parse(cls, value):
        """Parses JSON options from the respective value."""

        serialize = None
        deserialize = None

        if isinstance(value, (tuple, list)):
            try:
                key, serialize, deserialize = value
            except ValueError:
                try:
                    key, serialize = value
                except ValueError:
                    try:
                        key, = value
                    except ValueError:
                        raise ValueError(value)
        elif isinstance(value, str):
            key = value
        else:
            raise ValueError(value)

        return cls(key, serialize, deserialize)


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
            value = model.JSON_FIELDS[attribute]
        except KeyError:
            continue

        yield (attribute, field, JSONOptions.parse(value))


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
