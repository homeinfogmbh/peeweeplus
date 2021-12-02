"""Database enhancements."""

from __future__ import annotations
from configparser import ConfigParser
from logging import getLogger
from pathlib import Path
from typing import Any, Union

from peewee import SENTINEL, OperationalError, MySQLDatabase


__all__ = ['MySQLDatabase', 'MySQLDatabaseProxy']


class MySQLDatabase(MySQLDatabase):     # pylint: disable=E0102,W0223
    """Extension of peewee.MySQLDatabase with closing option."""

    # pylint: disable=W0221
    def execute_sql(self, sql: str, params: Any = None,
                    commit: Union[bool, object] = SENTINEL, *,
                    retry: bool = True):
        """Conditionally execute the SQL query in an
        execution context iff closing is enabled.
        """
        try:
            return super().execute_sql(sql, params=params, commit=commit)
        except OperationalError:
            if not retry:
                raise

        if not self.is_closed():
            self.close()

        return self.execute_sql(sql, params=params, commit=commit, retry=False)


class MySQLDatabaseProxy:
    """Proxies to a MySQL database."""

    def __init__(self, database: str, config_file: Union[Path, str],
                 config_section: str = 'db'):
        self.database = database
        self.config_file = config_file
        self.config_section = config_section
        self._database = MySQLDatabase(database)
        self._initialized = False

    def __getattr__(self, attribute: str) -> Any:
        """Delegates to the database while ensuring
        to load the config file beforehand.
        """
        if not self._initialized:
            self._initialize()

        return getattr(self._database, attribute)

    def _initialize(self) -> None:
        """Initializes the database."""
        getLogger(type(self).__name__).debug(
            'Loading database config from "%s" section "%s"', self.config_file,
            self.config_section)
        config_parser = ConfigParser()
        config_parser.read(self.config_file)
        self._database.init(
            self.database,
            host=config_parser.get(self.config_section, 'host'),
            user=config_parser.get(self.config_section, 'user'),
            passwd=config_parser.get(self.config_section, 'passwd')
        )
        self._initialized = True
