"""JSON serialization."""

from base64 import b64encode

from peewee import DecimalField, DateTimeField, DateField, TimeField, \
    BlobField
from peeweeplus.fields import EnumField, UUID4Field, IPv4AddressField
from peeweeplus.json.misc import serialization_filter, FieldMap


__all__ = ['serialize']


_FIELD_MAP = FieldMap(
    (DecimalField, float),
    ((DateTimeField, DateField, TimeField), lambda value: value.isoformat()),
    (BlobField, b64encode),
    (EnumField, lambda value: value.value),
    (UUID4Field, lambda value: value.hex),
    (IPv4AddressField, str))


def serialize(record, *, allow=(), deny=(), null=False, autofields=True):
    """Returns a JSON-ish dictionary with the record's values."""

    return {
        key: _FIELD_MAP.convert(field, value) for key, field, value
        in serialization_filter(
            record, allow=allow, deny=deny, null=null, autofields=autofields)}
