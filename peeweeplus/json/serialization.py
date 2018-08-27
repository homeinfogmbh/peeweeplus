"""JSON serialization."""

from base64 import b64encode

from peewee import AutoField, ForeignKeyField, DecimalField, DateTimeField, \
    DateField, TimeField, BlobField, UUIDField
from peeweeplus.fields import EnumField, PasswordField, IPv4AddressField
from peeweeplus.json.fields import contained, json_fields, FieldConverter


__all__ = ['serialize']


CONVERTER = FieldConverter(
    (AutoField, lambda value: value._pk),   # pylint: disable=W0212
    (DecimalField, float),
    ((DateTimeField, DateField, TimeField), lambda value: value.isoformat()),
    (BlobField, b64encode),
    (EnumField, lambda value: value.value),
    (UUIDField, lambda value: value.hex),
    (IPv4AddressField, str))


def serialize(record, *, null=False, skip=None, fk_fields=True,
              autofields=True):
    """Returns a JSON-ish dictionary with the record's values."""

    json = {}

    for key, field in json_fields(type(record)):
        if contained(key, skip):
            continue
        elif isinstance(field, PasswordField):
            continue
        elif not autofields and isinstance(field, AutoField):
            continue
        elif not fk_fields and isinstance(field, ForeignKeyField):
            continue

        value = getattr(record, field.name)
        json_value = CONVERTER(field, value, check_null=False)

        if json_value is None and not null:
            continue

        json[key] = json_value

    return json
