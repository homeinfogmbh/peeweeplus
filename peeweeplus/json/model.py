"""Base model with serialization and deserialization methods."""

from peewee import Model

from peeweeplus.json.deserialization import deserialize
from peeweeplus.json.serialization import serialize


__all__ = ['JSONModel']


class JSONModel(Model):
    """A JSON serializable and deserializable model."""

    from_dict = classmethod(deserialize)
    patch = deserialize
    to_dict = serialize
