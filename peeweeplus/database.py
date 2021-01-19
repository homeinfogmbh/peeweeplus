"""Database enhancements."""

from __future__ import annotations
from configparser import SectionProxy
from typing import Any

from peewee import OperationalError, MySQLDatabase


__all__ = ['MySQLDatabase']


class MySQLDatabase(MySQLDatabase):     # pylint: disable=E0102,W0223
    """Extension of peewee.MySQLDatabase with closing option."""

    def __init__(self, *args, retry: bool = False, **kwargs):
        """Adds closing switch for automatic connection closing."""
        super().__init__(*args, **kwargs)
        self.retry = retry

    @classmethod
    def from_config(cls, section: SectionProxy, *,
                    retry: bool = True) -> MySQLDatabase:
        """Creates a database from the respective configuration."""
        try:
            database = section['db']
        except KeyError:
            database = section['database']

        try:
            passwd = section['passwd']
        except KeyError:
            passwd = section['password']

        retry = section.getboolean('retry', retry)

        return cls(
            database, host=section['host'], user=section['user'],
            passwd=passwd, retry=retry)

    # pylint: disable=W0221
    def execute_sql(self, *args, retry: bool = True, **kwargs) -> Any:
        """Conditionally execute the SQL query in an
        execution context iff closing is enabled.
        """
        try:
            return super().execute_sql(*args, **kwargs)
        except OperationalError:
            if not self.retry or not retry:
                raise

        if not self.is_closed():
            self.close()

        return self.execute_sql(*args, retry=False, **kwargs)
