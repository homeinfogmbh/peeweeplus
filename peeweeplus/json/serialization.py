"""JSON serialization."""

from base64 import b64encode

from peewee import BlobField
from peewee import DateField
from peewee import DateTimeField
from peewee import DecimalField
from peewee import ForeignKeyField
from peewee import TimeField
from peewee import UUIDField
from peeweeplus.fields import EnumField, IPv4AddressField
from peeweeplus.json.fields import json_fields, FieldConverter
from peeweeplus.json.filter import FieldsFilter
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


def serialize(record, *, null=False, cascade=False, **filters):
    """Returns a JSON-ish dict with the record's fields' values."""

    model = type(record)
    fields = json_fields(model)
    fields_filter = FieldsFilter.for_serialization(**filters)
    json = {}

    for key, attribute, field in fields_filter.filter(fields):
        value = getattr(record, attribute)
        value = CONVERTER(field, value, check_null=False)

        if cascade and isinstance(field, ForeignKeyField):
            cascade = True if cascade is True else cascade - 1
            rel_model = field.rel_model

            try:
                rrec = rel_model[value]
            except rel_model.DoesNotExist:
                pass
            else:
                value = rrec.to_json(null=null, cascade=cascade, **filters)

        if not null and value is None:
            continue

        json[key] = value

    return json
