"""JSON deserialization."""

from ipaddress import IPv4Address
from uuid import UUID

from peewee import Model, BooleanField, IntegerField, FloatField, \
    DecimalField, DateTimeField, DateField, TimeField, BlobField

from peeweeplus.exceptions import NullError, FieldNotNullable, FieldValueError
from peeweeplus.fields import UUID4Field, IPv4AddressField
from peeweeplus.json.misc import deserialization_filter, FieldMap
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


def deserialize(target, dictionary, *, allow=(), deny=(), strict=True):
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

    for attribute, field, key, value in deserialization_filter(
            model, dictionary, patch, allow=allow, deny=deny, strict=strict):
        try:
            field_value = _FIELD_MAP.convert(field, value, check_null=True)
        except NullError:
            raise FieldNotNullable(model, attribute, field, key)
        except (TypeError, ValueError):
            raise FieldValueError(model, attribute, field, key, value)

        setattr(record, attribute, field_value)

    return record
