"""Databse proxies."""

from configparser import ConfigParser
from logging import getLogger
from pathlib import Path
from typing import Any, Optional, Union

from configlib import search_paths

from peeweeplus.database import MySQLDatabase


__all__ = ['DatabaseProxy', 'MySQLDatabaseProxy']


LOGGER = getLogger(__file__)


class DatabaseProxy:   # pylint: disable=R0903
    """Proxies to a MySQL database."""

    def __init__(self, typ: type, database: str,
                 config_file: Optional[Union[Path, str]] = None,
                 config_section: str = 'db'):
        self.database = database
        self.config_file = config_file or f'{database}.conf'
        self.config_section = config_section
        self._database = typ(database)
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
        LOGGER.debug('Loading database config from "%s" section "%s".',
                     self.config_file, self.config_section)
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


class MySQLDatabaseProxy(DatabaseProxy):
    """A MySQL database proxy."""

    def __init__(self, database: str,
                 config_file: Optional[Union[Path, str]] = None,
                 config_section: str = 'db'):
        super().__init__(MySQLDatabase, database, config_file, config_section)
