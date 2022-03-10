"""JSON deserialization."""

from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Any, Type
from uuid import UUID

from peewee import BlobField
from peewee import BooleanField
from peewee import CharField
from peewee import DateField
from peewee import DateTimeField
from peewee import DecimalField
from peewee import Field
from peewee import FloatField
from peewee import ForeignKeyField
from peewee import IntegerField
from peewee import Model
from peewee import TimeField
from peewee import UUIDField

from peeweeplus.exceptions import FieldNotNullable
from peeweeplus.exceptions import FieldValueError
from peeweeplus.exceptions import InvalidKeys
from peeweeplus.exceptions import MissingKeyError
from peeweeplus.exceptions import NonUniqueValue
from peeweeplus.exceptions import NullError
from peeweeplus.fields import EnumField
from peeweeplus.fields import IPAddressField
from peeweeplus.fields import IPv4AddressField
from peeweeplus.fields import IPv6AddressField
from peeweeplus.json.fields import get_json_fields, FieldConverter
from peeweeplus.json.filter import FieldsFilter
from peeweeplus.json.parsers import parse_blob
from peeweeplus.json.parsers import parse_char_field
from peeweeplus.json.parsers import parse_bool
from peeweeplus.json.parsers import parse_date
from peeweeplus.json.parsers import parse_datetime
from peeweeplus.json.parsers import parse_time
from peeweeplus.json.parsers import parse_enum
from peeweeplus.types import JSON


__all__ = ['deserialize', 'patch']


CONVERTER = FieldConverter({
    BlobField: parse_blob,
    BooleanField: parse_bool,
    CharField: parse_char_field,
    DateField: parse_date,
    DateTimeField: parse_datetime,
    DecimalField: float,
    EnumField: parse_enum,
    FloatField: float,
    ForeignKeyField: int,
    IntegerField: int,
    IPAddressField: ip_address,
    IPv4AddressField: IPv4Address,
    IPv6AddressField: IPv6Address,
    TimeField: parse_time,
    UUIDField: UUID
})


def get_orm_value(
        model: Type[Model],
        key: str,
        attribute: str,
        field: Field,
        json: JSON
) -> Any:
    """Returns the appropriate value for the field."""

    try:
        return CONVERTER(field, json, check_null=True)
    except NullError:
        raise FieldNotNullable(model, key, attribute, field) from None
    except (TypeError, ValueError):
        raise FieldValueError(model, key, attribute, field, json) from None


def is_unique(record: Model, field, orm_value) -> bool:
    """Checks whether the value is unique for the field."""

    model = field.model
    select = field == orm_value

    if (primary_key := record._pk) is not None:
        pk_field = model._meta.primary_key
        select &= pk_field != primary_key   # Exclude the model itself.

    try:
        model.get(select)
    except model.DoesNotExist:
        return True

    return False


def deserialize(
        model: Type[Model],
        json: dict,
        *,
        strict: bool = True,
        **filters
) -> Model:
    """Creates a new record from a JSON-ish dict."""

    record = model()
    fields = get_json_fields(model)
    json = dict(json)
    fields_filter = FieldsFilter.for_deserialization(**filters)

    for key, attribute, field in fields_filter.filter(fields):
        try:
            json_value = json.pop(key)
        except KeyError:
            # On missing key, skip if field is nullable or field has a default.
            if field.null or field.default is not None:
                continue

            raise MissingKeyError(model, key, attribute, field) from None

        orm_value = get_orm_value(model, key, attribute, field, json_value)

        if field.unique and not is_unique(record, field, orm_value):
            raise NonUniqueValue(key, json_value)

        setattr(record, attribute, orm_value)

    if json and strict:
        raise InvalidKeys(json.keys())

    return record


def patch(
        record: Model,
        json: dict,
        *,
        strict: bool = True,
        **filters
) -> None:
    """Patches an existing record with a JSON-ish dict."""

    model = type(record)
    fields = get_json_fields(model)
    json = dict(json)
    fields_filter = FieldsFilter.for_deserialization(**filters)

    for key, attribute, field in fields_filter.filter(fields):
        try:
            json_value = json.pop(key)
        except KeyError:
            continue

        orm_value = get_orm_value(model, key, attribute, field, json_value)

        if field.unique and not is_unique(record, field, orm_value):
            raise NonUniqueValue(key, json_value)

        setattr(record, attribute, orm_value)

    if json and strict:
        raise InvalidKeys(json.keys())
