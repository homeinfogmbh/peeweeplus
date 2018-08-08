"""JSON deserialization."""

from ipaddress import IPv4Address
from uuid import UUID

from peewee import Model, ForeignKeyField, BooleanField, IntegerField, \
    FloatField, DecimalField, DateTimeField, DateField, TimeField, BlobField

from peeweeplus.exceptions import NullError, FieldNotNullable, InvalidKeys, \
    MissingKeyError, FieldValueError
from peeweeplus.fields import UUID4Field, IPv4AddressField
from peeweeplus.json.misc import json_fields, json_key, FieldConverter
from peeweeplus.json.parsers import parse_bool, parse_datetime, parse_date, \
    parse_time, parse_blob


__all__ = ['deserialize']


_CONVERTER = FieldConverter(
    (ForeignKeyField, int),
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


def _filter(model, dictionary, patch, allow=(), deny=(), fk_fields=True,
            strict=True):
    """Filters the respective fields, yielding
        (<attribute>, <field>, <key>, <value>)
    tuples.
    """

    invalid_keys = set()
    allowed_keys = set()

    for attribute, field in json_fields(
            model, fk_fields=fk_fields, autofields=False):
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


def deserialize(target, dictionary, *, allow=(), deny=(), fk_fields=True,
                strict=True):
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

    record = target if patch else model()

    for attribute, field, key, value in _filter(
            model, dictionary, patch, fk_fields=fk_fields, allow=allow,
            deny=deny, strict=strict):
        try:
            field_value = _CONVERTER(field, value, check_null=True)
        except NullError:
            raise FieldNotNullable(model, attribute, field, key)
        except (TypeError, ValueError):
            raise FieldValueError(model, attribute, field, key, value)

        setattr(record, attribute, field_value)

    return record
