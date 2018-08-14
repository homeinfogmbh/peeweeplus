"""JSON serialization."""

from base64 import b64encode

from peewee import AutoField, ForeignKeyField, DecimalField, DateTimeField, \
    DateField, TimeField, BlobField
from peeweeplus.fields import EnumField, UUID4Field, IPv4AddressField
from peeweeplus.json.fields import json_fields, FieldConverter


__all__ = ['serialize']


_CONVERTER = FieldConverter(
    (ForeignKeyField, lambda model: model._pk),     # pylint: disable=W0212
    (DecimalField, float),
    ((DateTimeField, DateField, TimeField), lambda value: value.isoformat()),
    (BlobField, b64encode),
    (EnumField, lambda value: value.value),
    (UUID4Field, lambda value: value.hex),
    (IPv4AddressField, str))


def fields(model, fk_fields=False, autofields=True):
    """Yields the fields for serialization."""

    for attribute, field, options in json_fields(model):
        if options.serialize is None:
            if isinstance(field, AutoField) and not autofields:
                continue
            elif isinstance(field, ForeignKeyField) and not fk_fields:
                continue
        elif not options.serialize:
            continue

        yield (attribute, field, options.key)


def serialize(record, *, null=False, fk_fields=False, autofields=True):
    """Returns a JSON-ish dictionary with the record's values."""

    dictionary = {}

    for attribute, field, key in fields(type(record), fk_fields, autofields):
        value = getattr(record, attribute)
        json_value = _CONVERTER(field, value, check_null=False)

        if json_value is None and not null:
            continue

        dictionary[key] = json_value

    return dictionary
