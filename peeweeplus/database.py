"""Database enhancements."""

from logging import getLogger
from typing import Any

from peewee import MySQLDatabase as _MySQLDatabase


__all__ = ['MySQLDatabase']


LOGGER = getLogger(__file__)


class MySQLDatabase(_MySQLDatabase):
    """Extension of peewee.MySQLDatabase with closing option."""

    def execute_sql(self, *args, **kwargs) -> Any:
        """Conditionally execute the SQL query in an
        execution context iff closing is enabled.
        """
        if self._state.transactions:
            return super().execute_sql(*args, **kwargs)

        with self.connection_context():
            return super().execute_sql(*args, **kwargs)
