"""JSON serialization and deserialization."""

from base64 import b64decode, b64encode
from contextlib import suppress
from datetime import datetime, date, time
from ipaddress import IPv4Address

from peewee import Model, Field, AutoField, ForeignKeyField, BooleanField, \
    IntegerField, FloatField, DecimalField, DateTimeField, DateField, \
    TimeField, BlobField

from timelib import strpdatetime, strpdate, strptime

from peeweeplus.exceptions import FieldValueError, FieldNotNullable, \
    MissingKeyError, InvalidKeys, NotAField
from peeweeplus.fields import EnumField, UUID4Field, PasswordField, \
    IPv4AddressField


__all__ = ['json_names', 'deserialize', 'serialize', 'JSONModel']


class _NullError(TypeError):
    """Indicates that the respective field cannot be null."""

    pass


def _json_key(field):
    """Returns the key for JSON serialization."""

    try:
        return field.json_key
    except AttributeError:
        return field.column_name


def _json_fields(model, autofields=True):
    """Yields JSON name, attribute name and field
    instance for each field  of the model.
    """

    for attribute, field in model._meta.fields.items():
        # Skip hidden fields.
        if attribute.startswith('_'):
            continue

        # Forbidden fields.
        if isinstance(field, (ForeignKeyField, PasswordField)):
            continue

        if not autofields and isinstance(field, AutoField):
            continue

        yield (attribute, field)


def _field_to_json(field, value):
    """Converts the given field's value into JSON-ish data."""

    if value is None:
        return None

    if isinstance(field, DecimalField):
        return float(value)

    if isinstance(field, (DateTimeField, DateField, TimeField)):
        return value.isoformat()

    if isinstance(field, BlobField):
        return b64encode(value)

    if isinstance(field, EnumField):
        return value.value

    if isinstance(field, UUID4Field):
        return value.hex

    if isinstance(field, IPv4AddressField):
        return str(value)

    return value


def _value_to_field(value, field):
    """Converts a value for the provided field."""

    if value is None:
        if not field.null:
            raise _NullError()

        return None

    if isinstance(field, BooleanField):
        if isinstance(value, (bool, int)):
            return bool(value)

        raise ValueError(value)

    if isinstance(field, IPv4AddressField):
        return IPv4Address(value)

    if isinstance(field, IntegerField):
        return int(value)

    if isinstance(field, FloatField):
        return float(value)

    if isinstance(field, DecimalField):
        return float(value)

    if isinstance(field, DateTimeField):
        if isinstance(value, datetime):
            return value

        return strpdatetime(value)

    if isinstance(field, DateField):
        if isinstance(value, date):
            return value

        return strpdate(value)

    if isinstance(field, TimeField):
        if isinstance(value, time):
            return value

        return strptime(value)

    if isinstance(field, BlobField):
        if isinstance(value, bytes):
            return value

        return b64decode(value)

    return value


def _dict_items(record, fields, only, ignore, null):
    """Yields the respective dictionary items."""

    for attribute, field in fields:
        key = _json_key(field)

        if only is not None and (key, attribute, field) not in only:
            continue

        if ignore is not None and (key, attribute, field) in ignore:
            continue

        value = getattr(record, attribute)

        if value is not None or null:
            yield (key, _field_to_json(field, value))


def deserialize(target, dictionary, *, strict=True, allow=(), deny=()):
    """Applies the provided dictionary onto the target.
    The target can either be a Model subclass (deserialization)
    or a Model instance (patching).
    """

    if isinstance(target, Model):
        model = target.__class__
        patch = True
    elif issubclass(target, Model):
        model = target
        patch = False
    else:
        raise TypeError(target)

    allowed_keys = {
        _json_key(field) for _, field in _json_fields(model, autofields=False)}
    allowed_keys |= set(allow)
    allowed_keys -= set(deny)
    invalid_keys = set(key for key in dictionary if key not in allowed_keys)

    if invalid_keys and strict:
        raise InvalidKeys(invalid_keys)

    record = target if patch else model()

    for attribute, field in _json_fields(model, autofields=False):
        key = _json_key(field)

        try:
            value = dictionary[key]
        except KeyError:
            if not patch and field.default is None and not field.null:
                raise MissingKeyError(model, attribute, field, key)

            continue

        try:
            field_value = _value_to_field(value, field)
        except _NullError:
            raise FieldNotNullable(model, attribute, field, key)
        except (TypeError, ValueError):
            raise FieldValueError(model, attribute, field, key, value)

        setattr(record, attribute, field_value)

    return record


def serialize(record, *, only=None, ignore=None, null=False, autofields=True):
    """Returns a JSON-ish dictionary with the record's values."""

    if only is not None:
        only = _FieldList(only)

    if ignore is not None:
        ignore = _FieldList(ignore)

    json_fields_ = _json_fields(record.__class__, autofields=autofields)
    return dict(_dict_items(record, json_fields_, only, ignore, null))


def json_names(dictionary):
    """Decorator factory to serialize fields to the provided names."""

    def decorator(model):
        """The actual decorator."""
        keys = set()

        for attribute, key in dictionary.items():
            if key in keys:
                raise KeyError('Duplicate JSON key: {}.'.format(key))

            keys.add(key)
            field = getattr(model, attribute)

            if not isinstance(field, Field):
                raise NotAField(model, field)

            field.json_key = key

        return model

    return decorator


class _FieldList:
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


class JSONModel(Model):
    """A JSON serializable and deserializable model."""

    from_dict = classmethod(deserialize)
    patch = deserialize
    to_dict = serialize
