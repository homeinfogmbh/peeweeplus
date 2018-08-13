"""JSON deserialization."""

from ipaddress import IPv4Address
from uuid import UUID

from peewee import Model, AutoField, ForeignKeyField, BooleanField, \
    IntegerField, FloatField, DecimalField, DateTimeField, DateField, \
    TimeField, BlobField

from peeweeplus.exceptions import NullError, FieldNotNullable, InvalidKeys, \
    MissingKeyError, FieldValueError
from peeweeplus.fields import UUID4Field, IPv4AddressField
from peeweeplus.json.fields import json_fields, FieldConverter
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


def fields(model, fk_fields=False):
    """Yields fields for deserialization."""

    for attribute, field in json_fields(model):
        if field.deserialize is None:
            if isinstance(field, AutoField):
                continue

            if isinstance(field, ForeignKeyField) and not fk_fields:
                continue
        elif not field.deserialize:
            continue

        yield (attribute, field)


def deserialize(target, dictionary, *, fk_fields=False, strict=True):
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

    for attribute, field in fields(model, fk_fields=fk_fields):
        try:
            value = dictionary.pop(field.key)
        except KeyError:
            if not patch and field.default is None and not field.null:
                raise MissingKeyError(model, attribute, field, field.key)

            continue

        try:
            field_value = _CONVERTER(field, value, check_null=True)
        except NullError:
            raise FieldNotNullable(model, attribute, field, field.key)
        except (TypeError, ValueError):
            raise FieldValueError(model, attribute, field, field.key, value)

        setattr(record, attribute, field_value)

    if strict and dictionary:
        raise InvalidKeys(dictionary.keys())

    return record
