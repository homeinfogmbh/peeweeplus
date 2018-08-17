"""Base model with serialization and deserialization methods."""

from peewee import Model

from peeweeplus.json.deserialization import deserialize
from peeweeplus.json.fields import json_fields
from peeweeplus.json.serialization import serialize


__all__ = ['JSONModel']


class JSONModel(Model):
    """A JSON serializable and deserializable model."""

    json_fields = classmethod(json_fields)
    from_json = classmethod(deserialize)
    patch_json = deserialize
    to_json = serialize
