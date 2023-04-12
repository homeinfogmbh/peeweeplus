"""Database proxies."""

from configparser import ConfigParser
from logging import getLogger
from pathlib import Path
from typing import Any, Optional, Type, Union

from peewee import Database

from configlib import search_paths

from peeweeplus.database import MySQLDatabase


__all__ = ['DatabaseProxy', 'MySQLDatabaseProxy']


LOGGER = getLogger(__file__)


class DatabaseProxy:
    """Proxies to a MySQL database."""

    def __init__(
            self,
            database: str,
            config_file: Optional[Union[Path, str]] = None,
            config_section: str = 'db'
    ):
        self.database = database
        self.config_file = config_file or f'{database}.conf'
        self.config_section = config_section
        self._database = self._dbtype(database)
        self._initialized = False

    def __init_subclass__(cls, *, dbtype: Optional[Type[Database]] = None):
        if dbtype is not None:
            cls._dbtype = dbtype

    def __getattr__(self, attribute: str) -> Any:
        """Delegates to the database while ensuring
        to load the config file beforehand.
        """
        if not self._initialized:
            self._initialize()

        return getattr(self._database, attribute)

    def _initialize(self) -> None:
        """Initializes the database."""
        LOGGER.debug(
            'Loading database config from "%s" section "%s".',
            self.config_file, self.config_section
        )
        config = ConfigParser()

        for filename in search_paths(self.config_file):
            config.read(filename)

        self._database.init(
            database := self.database,
            host=config.get(self.config_section, 'host', fallback='localhost'),
            user=config.get(self.config_section, 'user', fallback=database),
            passwd=config.get(self.config_section, 'passwd'),
            charset=config.get(
                self.config_section,
                'charset',
                fallback='utf8mb4'
            )
        )
        self._initialized = True


class MySQLDatabaseProxy(DatabaseProxy, dbtype=MySQLDatabase):
    """A MySQL database proxy."""
