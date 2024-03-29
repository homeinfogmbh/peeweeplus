"""Datetime-related fields."""

from datetime import timedelta
from typing import Optional

from peewee import FloatField


__all__ = ["TimedeltaField"]


class TimedeltaField(FloatField):
    """A field that stores a timedelta in seconds."""

    def db_value(self, value: Optional[timedelta]) -> Optional[float]:
        """Returns the database value as float of seconds."""
        if value is None:
            return None

        return value.total_seconds()

    def python_value(self, value: Optional[float]) -> Optional[timedelta]:
        """Returns the python value as timedelta."""
        if value is None:
            return None

        return timedelta(seconds=value)
