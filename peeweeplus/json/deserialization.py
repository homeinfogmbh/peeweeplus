"""JSON deserialization."""

from ipaddress import IPv4Address
from uuid import UUID

from peewee import Model, BooleanField, IntegerField, FloatField, \
    DecimalField, DateTimeField, DateField, TimeField, BlobField

from peeweeplus.exceptions import NullError, InvalidKeys, MissingKeyError, \
    FieldNotNullable, FieldValueError
from peeweeplus.fields import UUID4Field, IPv4AddressField
from peeweeplus.json.misc import json_fields, json_key, FieldMap
from peeweeplus.json.parsers import parse_bool, parse_datetime, parse_date, \
    parse_time, parse_blob


__all__ = ['deserialize']


_FIELD_MAP = FieldMap(
    (BooleanField, parse_bool),
    (UUID4Field, UUID),
    (IPv4AddressField, IPv4Address),
    (IntegerField, int),
    (FloatField, float),
    (DecimalField, float),
    (DateTimeField, parse_datetime),
    (DateField, parse_date),
    (TimeField, parse_time),
    (BlobField, parse_blob))


def deserialize(target, dictionary, *, strict=True, allow=(), deny=()):
    """Applies the provided dictionary onto the target.
    The target can either be a Model subclass (deserialization)
    or a Model instance (patching).
    """

    if isinstance(target, Model):
        model = type(target)
        patch = True
    elif issubclass(target, Model):
        model = target
        patch = False
    else:
        raise TypeError(target)

    allowed_keys = {json_key(field) for _, field in json_fields(
        model, autofields=False)}
    allowed_keys |= set(allow)
    allowed_keys -= set(deny)
    invalid_keys = set(key for key in dictionary if key not in allowed_keys)

    if invalid_keys and strict:
        raise InvalidKeys(invalid_keys)

    record = target if patch else model()

    for attribute, field in json_fields(model, autofields=False):
        key = json_key(field)

        try:
            value = dictionary[key]
        except KeyError:
            if not patch and field.default is None and not field.null:
                raise MissingKeyError(model, attribute, field, key)

            continue

        try:
            field_value = _FIELD_MAP.convert(field, value)
        except NullError:
            raise FieldNotNullable(model, attribute, field, key)
        except (TypeError, ValueError):
            raise FieldValueError(model, attribute, field, key, value)

        setattr(record, attribute, field_value)

    return record
