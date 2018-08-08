"""JSON serialization."""

from base64 import b64encode

from peewee import DecimalField, DateTimeField, DateField, TimeField, \
    BlobField
from peeweeplus.fields import EnumField, UUID4Field, IPv4AddressField
from peeweeplus.json.misc import json_fields, json_key, FieldMap


__all__ = ['serialize']


_FIELD_MAP = FieldMap(
    (DecimalField, float),
    ((DateTimeField, DateField, TimeField), lambda value: value.isoformat()),
    (BlobField, b64encode),
    (EnumField, lambda value: value.value),
    (UUID4Field, lambda value: value.hex),
    (IPv4AddressField, str))


def _filter(record, allow=(), deny=(), null=False, autofields=True):
    """Yields the respective dictionary items in the form of
    (<key>, <field>, <value>).
    """

    for attribute, field in json_fields(type(record), autofields=autofields):
        key = json_key(field)

        if allow and key not in allow:
            continue

        if deny and key in deny:
            continue

        value = getattr(record, attribute)

        if value is not None or null:
            yield (key, field, value)


def serialize(record, *, allow=(), deny=(), null=False, autofields=True):
    """Returns a JSON-ish dictionary with the record's values."""

    return {
        key: _FIELD_MAP.convert(field, value) for key, field, value in _filter(
            record, allow=allow, deny=deny, null=null, autofields=autofields)}
