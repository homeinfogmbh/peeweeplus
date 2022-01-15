"""Database enhancements."""

from logging import getLogger
from typing import Any

from peewee import OperationalError, MySQLDatabase


__all__ = ['MySQLDatabase']


LOGGER = getLogger(__file__)


class MySQLDatabase(MySQLDatabase):     # pylint: disable=E0102,W0223
    """Extension of peewee.MySQLDatabase with closing option."""

    # pylint: disable=W0221
    def execute_sql(self, *args, **kwargs) -> Any:
        """Conditionally execute the SQL query in an
        execution context iff closing is enabled.
        """
        with self.connection_context():
            return super().execute_sql(*args, **kwargs)
