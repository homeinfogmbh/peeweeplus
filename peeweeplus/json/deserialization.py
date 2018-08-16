"""JSON deserialization."""

from ipaddress import IPv4Address
from uuid import UUID

from peewee import Model, AutoField, ForeignKeyField, BooleanField, \
    IntegerField, FloatField, DecimalField, DateTimeField, DateField, \
    TimeField, BlobField, UUIDField

from peeweeplus.exceptions import NullError, FieldNotNullable, InvalidKeys, \
    MissingKeyError, FieldValueError
from peeweeplus.fields import IPv4AddressField
from peeweeplus.json.fields import json_fields, FieldConverter
from peeweeplus.json.parsers import parse_bool, parse_datetime, parse_date, \
    parse_time, parse_blob


__all__ = ['deserialize']


CONVERTER = FieldConverter(
    (ForeignKeyField, int),
    (BooleanField, parse_bool),
    (UUIDField, UUID),
    (IPv4AddressField, IPv4Address),
    (IntegerField, int),
    (FloatField, float),
    (DecimalField, float),
    (DateTimeField, parse_datetime),
    (DateField, parse_date),
    (TimeField, parse_time),
    (BlobField, parse_blob))


def fields(model, *, skip=frozenset(), fk_fields=False):
    """Yields fields for deserialization."""

    for field in json_fields(model):
        if field.name in skip or field.json_key in skip:
            continue
        elif isinstance(field, AutoField):
            continue
        elif not fk_fields and isinstance(field, ForeignKeyField):
            continue

        yield field


def deserialize(target, dictionary, *, skip=frozenset(), fk_fields=False):
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
    dictionary = dict(dictionary)   # Shallow copy dictionary.

    for field in fields(model, skip=skip, fk_fields=fk_fields):
        try:
            value = dictionary.pop(field.json_key)
        except KeyError:
            if not patch and field.default is None and not field.null:
                raise MissingKeyError(model, field)

            continue

        try:
            field_value = CONVERTER(field, value, check_null=True)
        except NullError:
            raise FieldNotNullable(model, field)
        except (TypeError, ValueError):
            raise FieldValueError(model, field, value)

        setattr(record, field.name, field_value)

    if dictionary:
        raise InvalidKeys(dictionary.keys())

    return record
