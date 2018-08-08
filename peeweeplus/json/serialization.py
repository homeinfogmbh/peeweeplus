"""JSON serialization."""

from base64 import b64encode

from peewee import DecimalField, DateTimeField, DateField, TimeField, \
    BlobField
from peeweeplus.fields import EnumField, UUID4Field, IPv4AddressField
from peeweeplus.json.misc import json_fields, json_key, FieldList, FieldMap


__all__ = ['serialize']


_FIELD_MAP = FieldMap(
    (DecimalField, float),
    ((DateTimeField, DateField, TimeField), lambda value: value.isoformat()),
    (BlobField, b64encode),
    (EnumField, lambda value: value.value),
    (UUID4Field, lambda value: value.hex),
    (IPv4AddressField, str))


def _dict_items(record, fields, only, ignore, null):
    """Yields the respective dictionary items."""

    for attribute, field in fields:
        key = json_key(field)

        if only is not None and (key, attribute, field) not in only:
            continue

        if ignore is not None and (key, attribute, field) in ignore:
            continue

        value = getattr(record, attribute)

        if value is not None or null:
            yield (key, _FIELD_MAP.convert(field, value))


def serialize(record, *, only=None, ignore=None, null=False, autofields=True):
    """Returns a JSON-ish dictionary with the record's values."""

    if only is not None:
        only = FieldList(only)

    if ignore is not None:
        ignore = FieldList(ignore)

    fields = json_fields(type(record), autofields=autofields)
    return dict(_dict_items(record, fields, only, ignore, null))
