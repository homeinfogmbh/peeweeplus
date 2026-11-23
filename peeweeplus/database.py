"""Database enhancements."""

from logging import getLogger
from typing import Any

from peewee import MySQLDatabase as _MySQLDatabase


__all__ = ["MySQLDatabase"]


LOGGER = getLogger(__file__)


class MySQLDatabase(_MySQLDatabase):
    """Extension of peewee.MySQLDatabase with closing option."""

    def execute_sql(self, *args, **kwargs) -> Any:
        """Execute the SQL query.

        If a connection is already open (e.g. inside a transaction or a
        peeweeplus.connected() block), it is reused. Otherwise a connection
        is opened for this single query and closed again afterwards, so that
        no idle connections are left behind in long-running processes.
        """
        if self._state.transactions or not self.is_closed():
            return super().execute_sql(*args, **kwargs)

        with self.connection_context():
            return super().execute_sql(*args, **kwargs)
