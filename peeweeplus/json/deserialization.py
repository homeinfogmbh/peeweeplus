"""JSON deserialization."""

from ipaddress import IPv4Address
from uuid import UUID

from peewee import AutoField, ForeignKeyField, BooleanField, IntegerField, \
    FloatField, DecimalField, DateTimeField, DateField, TimeField, BlobField, \
    UUIDField

from peeweeplus.exceptions import NullError, FieldNotNullable, InvalidKeys, \
    MissingKeyError, FieldValueError, NonUniqueValue
from peeweeplus.fields import IPv4AddressField
from peeweeplus.json.fields import contains, json_fields, FieldConverter
from peeweeplus.json.parsers import parse_bool, parse_datetime, parse_date, \
    parse_time, parse_blob


__all__ = ['deserialize', 'patch']


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


def copy_dict(dictionary):
    """Returns a shallow copy of the dictionary."""

    try:
        return dict(dictionary)
    except TypeError:
        raise ValueError('JSON object must be a dictionary.')


def fields(model, skip=(), fk_fields=False):
    """Filters fields."""

    for key, attribute, field in json_fields(model):
        if contains(skip, key, attribute):
            continue
        elif isinstance(field, AutoField):
            continue
        elif not fk_fields and isinstance(field, ForeignKeyField):
            continue

        yield (key, attribute, field)


def get_orm_value(model, key, attribute, field, json_value):
    """Returns the appropriate value for the field."""

    try:
        return CONVERTER(field, json_value, check_null=True)
    except NullError:
        raise FieldNotNullable(model, key, attribute, field)
    except (TypeError, ValueError):
        raise FieldValueError(model, key, attribute, field, json_value)


def is_unique(record, field, orm_value):
    """Checks whether the value is unique for the field."""

    primary_key = record._pk    # pylint: disable=W0212
    model = field.model
    select = field == orm_value

    if primary_key is not None:
        pk_field = model._meta.primary_key  # pylint: disable=W0212
        select &= pk_field != primary_key   # Exclude the model itself.

    try:
        model.get(select)
    except model.DoesNotExist:
        return True

    return False


def deserialize(model, json, *, skip=None, fk_fields=False):
    """Creates a new record from a JSON-ish dict."""

    record = model()
    json = copy_dict(json)

    for key, attribute, field in fields(model, skip=skip, fk_fields=fk_fields):
        try:
            json_value = json.pop(key)
        except KeyError:
            # On missing key, skip if field is nullable or field has a default.
            if field.null or field.default is not None:
                continue

            raise MissingKeyError(model, key, attribute, field)

        orm_value = get_orm_value(model, key, attribute, field, json_value)

        if field.unique and not is_unique(record, field, orm_value):
            raise NonUniqueValue(key, json_value)

        setattr(record, attribute, orm_value)

    if json:
        raise InvalidKeys(json.keys())

    return record


def patch(record, json, *, skip=None, fk_fields=False):
    """Patches an existing record with a JSON-ish dict."""

    model = type(record)
    json = copy_dict(json)

    for key, attribute, field in fields(model, skip=skip, fk_fields=fk_fields):
        try:
            json_value = json.pop(key)
        except KeyError:
            continue

        orm_value = get_orm_value(model, key, attribute, field, json_value)

        if field.unique and not is_unique(record, field, orm_value):
            raise NonUniqueValue(key, json_value)

        setattr(record, attribute, orm_value)

    if json:
        raise InvalidKeys(json.keys())
