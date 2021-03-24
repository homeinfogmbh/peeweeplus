"""Database enhancements."""

from __future__ import annotations
from configparser import SectionProxy
from typing import Any, Optional, Union

from peewee import OperationalError, MySQLDatabase


__all__ = ['MySQLDatabase']


class MySQLDatabase(MySQLDatabase):     # pylint: disable=E0102,W0223
    """Extension of peewee.MySQLDatabase with closing option."""

    def init(self, database: str, *,
             config: Optional[Union[SectionProxy, dict]] = None,
             **kwargs) -> None:
        """Initializes the database."""
        self.config = config    # Must be done first!
        super().init(database, **kwargs)
        self.deferred = not (database or config)

    @property
    def database(self) -> Optional[str]:
        """Returns the database name."""
        if self.config is None:
            return self._database

        return self.config.get('db', fallback=self.config.get('database'))

    @database.setter
    def database(self, database: Optional[str]) -> None:
        """Sets the database name."""
        self._database = database

    @property
    def connect_params(self) -> dict:
        """Returns the connection parameters."""
        if self.config is None:
            return self._connect_params

        return {
            'host': self.config.get('host'),
            'user': self.config.get('user'),
            'passwd': self.config.get('passwd'),
            **self._connect_params
        }

    @connect_params.setter
    def connect_params(self, connect_params: dict) -> None:
        """Sets the connection parameters."""
        self._connect_params = connect_params

    @property
    def closing(self) -> bool:
        """Determines whether the database is auto-closing."""
        if self.config is None:
            return False

        try:
            return self.config.getboolean('closing', True)
        except AttributeError:
            return self.config.get('closing', True)

    @property
    def retry(self) -> bool:
        """Determines whether the database is auto-retrying."""
        if self.config is None:
            return False

        try:
            return self.config.getboolean('retry', False)
        except AttributeError:
            return self.config.get('retry', False)

    @classmethod
    def from_config(cls, config: SectionProxy) -> MySQLDatabase:
        """Creates a database from the respective configuration."""
        return cls(None, config=config)

    # pylint: disable=W0221
    def execute_sql(self, *args, retried: bool = False, **kwargs) -> Any:
        """Conditionally execute the SQL query in an
        execution context iff closing is enabled.
        """
        if self.closing:
            with self.connection_context():
                return super().execute_sql(*args, **kwargs)

        try:
            return super().execute_sql(*args, **kwargs)
        except OperationalError:
            if not self.retry or retried:
                raise

            if not self.is_closed():
                self.close()

            return self.execute_sql(*args, retried=True, **kwargs)
