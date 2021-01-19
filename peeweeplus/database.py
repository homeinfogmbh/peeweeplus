"""Database enhancements."""

from __future__ import annotations
from configparser import SectionProxy

from peewee import OperationalError, MySQLDatabase as _MySQLDatabase


__all__ = ['MySQLDatabase']


class MySQLDatabase(_MySQLDatabase):    # pylint: disable=W0223
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

    def execute_sql(self, *args, retried: bool = False, **kwargs):
        """Conditionally execute the SQL query in an
        execution context iff closing is enabled.
        """
        try:
            return super().execute_sql(*args, **kwargs)
        except OperationalError:
            if not self.retry or retried:
                raise

        if not self.is_closed():
            self.close()

        return self.execute_sql(*args, retried=True, **kwargs)
