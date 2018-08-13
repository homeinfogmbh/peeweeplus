"""Miscellaneous stuff."""

from functools import lru_cache

from peeweeplus.exceptions import NullError


__all__ = ['json_fields', 'JSONField', 'FieldConverter']


@lru_cache()
def _create_json_field(field_type):
    """Creates a JSON field from the given peewee field type."""

    def init(self, *args, serialize=None, deserialize=None, key=None,
             **kwargs):
        """The JSON field's __init__ method."""
        _JSONFieldMixin.__init__(
            self, serialize=serialize, deserialize=deserialize, key=key)
        field_type.__init__(self, *args, **kwargs)

    return type('JSON' + field_type.__name__, (field_type, _JSONFieldMixin), {
        '__init__': init})


def json_fields(model):
    """Yields JSON name, attribute name and field
    instance for each field  of the model.
    """

    for attribute, field in model._meta.fields.items():
        if isinstance(field, _JSONFieldMixin):
            yield (attribute, field)


def JSONField(field_type, *args, serialize=None, deserialize=None, key=None,
              **kwargs):
    """Factory to dynamically create JSON fields."""

    cls = _create_json_field(field_type)
    return cls(
        *args, serialize=serialize, deserialize=deserialize, key=key, **kwargs)


class _JSONFieldMixin:
    """Mixin for JSON serializable and deserializable fields."""

    def __init__(self, serialize=None, deserialize=None, key=None):
        """Sets the serialization and deserialization keys."""
        self.serialize = serialize
        self.deserialize = deserialize
        self._json_key = key
        self.column_name = NotImplemented

    @property
    def json_key(self):
        """returns the JSON key."""
        return self._json_key or self.column_name


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
