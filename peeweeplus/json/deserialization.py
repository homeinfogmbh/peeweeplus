"""JSON deserialization."""

from ipaddress import IPv4Address
from uuid import UUID

from peewee import Model, AutoField, ForeignKeyField, BooleanField, \
    IntegerField, FloatField, DecimalField, DateTimeField, DateField, \
    TimeField, BlobField, UUIDField

from peeweeplus.exceptions import NullError, FieldNotNullable, InvalidKeys, \
    MissingKeyError, FieldValueError
from peeweeplus.fields import IPv4AddressField
from peeweeplus.json.fields import contained, json_fields, FieldConverter
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


def deserialize(target, json, *, skip=None, fk_fields=False):
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

    try:
        json = dict(json)   # Shallow copy dictionary.
    except TypeError:
        raise ValueError('JSON object must be a dictionary.')

    for field, attribute, key in json_fields(model):
        if contained(key, skip):
            continue
        elif isinstance(field, AutoField):
            continue
        elif not fk_fields and isinstance(field, ForeignKeyField):
            continue

        try:
            value = json.pop(key)
        except KeyError:
            if not patch and field.default is None and not field.null:
                raise MissingKeyError(model, field, attribute, key)

            continue

        try:
            field_value = CONVERTER(field, value, check_null=True)
        except NullError:
            raise FieldNotNullable(model, field, attribute, key)
        except (TypeError, ValueError):
            raise FieldValueError(model, field, attribute, key, value)

        setattr(record, attribute, field_value)

    if json:
        raise InvalidKeys(json.keys())

    if patch:
        return None

    return record
