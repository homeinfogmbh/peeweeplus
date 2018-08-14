"""Miscellaneous stuff."""

from collections import namedtuple

from peeweeplus.exceptions import NullError


__all__ = ['json_fields', 'JSONOptions', 'FieldConverter']


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


def json_fields(model):
    """Yields JSON name, attribute name and field
    instance for each field  of the model.
    """

    fields = {}

    for cls in reversed(model.__mro__):
        fields.update(cls.__dict__.get('JSON_FIELDS', {}))

    for attribute, field in model._meta.fields.items():
        try:
            options = fields[field]
        except KeyError:
            continue

        yield (attribute, field, JSONOptions.parse(options))


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
