"""Database enhancements."""

from configparser import ConfigParser
from logging import getLogger
from pathlib import Path
from typing import Any, Optional, Union

from peewee import OperationalError, MySQLDatabase

from configlib import search_paths


__all__ = ['MySQLDatabase', 'MySQLDatabaseProxy']


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

        if not self.is_closed():
            self.close()

        return self.execute_sql(*args, retried=True, **kwargs)


class MySQLDatabaseProxy:   # pylint: disable=R0903
    """Proxies to a MySQL database."""

    def __init__(self, database: str,
                 config_file: Optional[Union[Path, str]] = None,
                 config_section: str = 'db'):
        self.database = database
        self.config_file = config_file or f'{database}.conf'
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
        config = ConfigParser()

        for filename in search_paths(self.config_file):
            config.read(filename)

        self._database.init(
            database := self.database,
            host=config.get(self.config_section, 'host', fallback='localhost'),
            user=config.get(self.config_section, 'user', fallback=database),
            passwd=config.get(self.config_section, 'passwd')
        )
        self._initialized = True
