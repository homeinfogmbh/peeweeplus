"""Text-based JSON storage."""

from json import loads, dumps
from typing import Callable, Optional

from peewee import TextField

from peeweeplus.types import JSON


__all__ = ["JSONTextField"]


class JSONTextField(TextField):
    """Stores JSON as text."""

    def __init__(
        self,
        *args,
        serialize: Callable[[JSON], str] = dumps,
        deserialize: Callable[[str], JSON] = loads,
        **kwargs
    ):
        """Sets the respective encoding and decoding functions."""
        super().__init__(*args, **kwargs)
        self.serialize = serialize
        self.deserialize = deserialize

    def db_value(self, value: JSON) -> Optional[str]:
        """Returns a string for the database."""
        if value is None:
            if self.null:
                return None

            return self.serialize(None)

        return self.serialize(value)

    def python_value(self, value: Optional[str]) -> JSON:
        """Returns a JSON object for python."""
        if value is None:
            return None

        return self.deserialize(value)
