"""Database enhancements."""

from configparser import ConfigParser
from logging import getLogger
from pathlib import Path
from typing import Any, Union

from peewee import OperationalError, MySQLDatabase


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
