"""JSON serialization and deserialization API."""

from peeweeplus.json.deserialization import deserialize
from peeweeplus.json.model import JSONModel
from peeweeplus.json.serialization import serialize


__all__ = ['deserialize', 'serialize', 'JSONModel']