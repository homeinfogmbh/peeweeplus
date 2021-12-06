"""Database enhancements."""

from logging import getLogger
from typing import Any

from peewee import OperationalError, MySQLDatabase


__all__ = ['MySQLDatabase']


LOGGER = getLogger(__file__)


class MySQLDatabase(MySQLDatabase):     # pylint: disable=E0102,W0223
    """Extension of peewee.MySQLDatabase with closing option."""

    # pylint: disable=W0221
    def execute_sql(self, *args, retried: bool = False, **kwargs) -> Any:
        """Conditionally execute the SQL query in an
        execution context iff closing is enabled.
        """
        try:
            return super().execute_sql(*args, **kwargs)
        except OperationalError:
            if retried:
                raise

            LOGGER.debug('Encountered an operational error. Retrying query.')

        if not self.is_closed():
            self.close()

        return self.execute_sql(*args, retried=True, **kwargs)
