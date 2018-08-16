"""JSON serialization."""

from base64 import b64encode

from peewee import AutoField, ForeignKeyField, DecimalField, DateTimeField, \
    DateField, TimeField, BlobField, UUIDField
from peeweeplus.fields import EnumField, IPv4AddressField
from peeweeplus.json.fields import json_fields, FieldConverter


__all__ = ['serialize']


CONVERTER = FieldConverter(
    (ForeignKeyField, lambda model: model._pk),     # pylint: disable=W0212
    (DecimalField, float),
    ((DateTimeField, DateField, TimeField), lambda value: value.isoformat()),
    (BlobField, b64encode),
    (EnumField, lambda value: value.value),
    (UUIDField, lambda value: value.hex),
    (IPv4AddressField, str))


def fields(model, *, skip=frozenset(), fk_fields=True, autofields=True):
    """Yields the fields for serialization."""

    for key, field in json_fields(model):
        if key in skip or field.name in skip:
            continue
        elif not autofields and isinstance(field, AutoField):
            continue
        elif not fk_fields and isinstance(field, ForeignKeyField):
            continue

        yield (key, field)


def serialize(record, *, null=False, skip=frozenset(), fk_fields=True,
              autofields=True):
    """Returns a JSON-ish dictionary with the record's values."""

    dictionary = {}

    for key, field in fields(
            type(record), skip=skip, fk_fields=fk_fields,
            autofields=autofields):
        value = getattr(record, field.name)
        json_value = CONVERTER(field, value, check_null=False)

        if json_value is None and not null:
            continue

        dictionary[key] = json_value

    return dictionary
