"""JSON serialization."""

from base64 import b64encode

from peewee import AutoField
from peewee import BlobField
from peewee import DateField
from peewee import DateTimeField
from peewee import DecimalField
from peewee import ForeignKeyField
from peewee import TimeField
from peewee import UUIDField
from peeweeplus.fields import EnumField, IPv4AddressField, PasswordField
from peeweeplus.json.fields import contains, json_fields, FieldConverter
from peeweeplus.json.parsers import get_fk_value


__all__ = ['serialize']


CONVERTER = FieldConverter(
    (ForeignKeyField, get_fk_value),
    (DecimalField, float),
    ((DateTimeField, DateField, TimeField), lambda value: value.isoformat()),
    (BlobField, b64encode),
    (EnumField, lambda value: value.value),
    (UUIDField, lambda value: value.hex),
    (IPv4AddressField, str))


def serialize(record, *, null=False, skip=None, fk_fields=True,
              autofields=True):
    """Returns a JSON-ish dict with the record's fields' values."""

    json = {}

    for key, attribute, field in json_fields(type(record)):
        if contains(skip, key, attribute):
            continue
        elif isinstance(field, PasswordField):
            continue
        elif not autofields and isinstance(field, AutoField):
            continue
        elif not fk_fields and isinstance(field, ForeignKeyField):
            continue

        value = getattr(record, attribute)
        json_value = CONVERTER(field, value, check_null=False)

        if json_value is None and not null:
            continue

        json[key] = json_value

    return json
