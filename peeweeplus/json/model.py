"""Base model with serialization and deserialization methods."""

from peewee import Model

from peeweeplus.json.deserialization import CONVERTER, deserialize
from peeweeplus.json.fields import json_fields
from peeweeplus.json.serialization import serialize


__all__ = ['JSONModel']


class JSONModel(Model):
    """A JSON serializable and deserializable model."""

    json_fields = classmethod(json_fields)
    from_json = classmethod(deserialize)
    patch_json = deserialize
    to_json = serialize

    @classmethod
    def json_select(cls, json, skip=None):
        """Selects from the model from the respective JSON dict."""
        skip = skip or frozenset()
        select = True

        for key, value in json.items():
            if key in skip:
                continue

            field = getattr(cls, key)
            value = CONVERTER(field, value, check_null=False)

            if value is None:
                select &= field >> None
            else:
                select &= field == value

        return cls.select().where(select)

    @classmethod
    def json_get(cls, json, skip=None):
        """Gets the first matched record from the respective JSON dict."""
        return cls.json_select(json, skip=skip).get()
