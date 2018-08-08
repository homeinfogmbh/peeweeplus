"""JSON serialization and deserialization related decorators."""

from peewee import Field

from peeweeplus.exceptions import NotAField


__all__ = ['json_names']


def json_names(dictionary):
    """Decorator factory to serialize fields to the provided names."""

    def decorator(model):
        """The actual decorator."""
        keys = set()

        for attribute, key in dictionary.items():
            if key in keys:
                raise KeyError('Duplicate JSON key: {}.'.format(key))

            keys.add(key)
            field = getattr(model, attribute)

            if not isinstance(field, Field):
                raise NotAField(model, field)

            field.json_key = key

        return model

    return decorator
