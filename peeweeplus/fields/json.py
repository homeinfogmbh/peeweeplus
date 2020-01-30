"""Text-based JSON storage."""

from json import loads, dumps

from peewee import TextField


__all__ = ['JSONTextField']


class JSONTextField(TextField):
    """Stores JSON as text."""

    def __init__(self, *args, serialize=dumps, deserialize=loads, **kwargs):
        """Sets the respective encoding and decoding functions."""
        super().__init__(*args, **kwargs)
        self.serialize = serialize
        self.deserialize = deserialize

    def db_value(self, value):
        """Returns a string for the database."""
        if value is None:
            if self.null:
                return None

            return self.serialize({})

        return self.serialize(value)

    def python_value(self, value):
        """Returns a JSON object for python."""
        if value is None:
            if self.null:
                return None

            return {}

        return self.deserialize(value)
