"""Base model with serialization and deserialization methods."""

from peewee import Model

from peeweeplus.json.deserialization import deserialize, patch
from peeweeplus.json.fields import get_json_fields
from peeweeplus.json.serialization import serialize


__all__ = ['JSONMixin', 'JSONModel']


class JSONMixin:    # pylint: disable=R0903
    """A JSON serializable and deserializable model mixin."""

    get_json_fields = classmethod(get_json_fields)
    from_json = classmethod(deserialize)
    patch_json = patch
    to_json = serialize


class JSONModel(Model, JSONMixin):
    """A JSON de-/serializable model."""
