"""Base model with serialization and deserialization methods."""

from peewee import Model

from peeweeplus.fields import PasswordField
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

    def __repr__(self):
        """Returns the service's name."""
        cls = type(self)
        fields = cls._meta.fields   # pylint: disable=E1101
        args = ', '.join(
            f'{name}=...' if isinstance(field, PasswordField)
            else f'{name}={getattr(self, name)!r}'
            for name, field in fields.items()
        )
        return f'{cls.__name__}({args})'
