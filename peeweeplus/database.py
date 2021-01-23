"""Database enhancements."""

from __future__ import annotations
from configparser import ConfigParser, SectionProxy
from typing import Any, Optional

from peewee import OperationalError, MySQLDatabase


__all__ = ['MySQLDatabase']


def params_from_config(config: SectionProxy) -> dict:
    """Returns the database params from the configuration."""

    return {
        'database': config.get('db', fallback=config.get('database')),
        'host': config.get('host'),
        'user': config.get('user'),
        'passwd': config.get('passwd', fallback=config.get('password')),
        'closing': config.getboolean('closing', True),
        'retry': config.getboolean('retry', False)
    }


class MySQLDatabase(MySQLDatabase):     # pylint: disable=E0102,W0223
    """Extension of peewee.MySQLDatabase with closing option."""

    def __init__(self, database: str, config: Optional[ConfigParser] = None,
                 **kwargs):
        """Calls __init__ of super and sets closing and retry flags."""
        super().__init__(database, **kwargs)
        self._config = config
        self._config_loaded = False

    @classmethod
    def from_config(cls, config: SectionProxy) -> MySQLDatabase:
        """Creates a database from the respective configuration."""
        return cls(**params_from_config(config))

    def init(self, database: str, closing: bool = False, retry: bool = False,
             **kwargs):
        """Invokes super's init method."""
        super().init(database, **kwargs)
        self.closing = closing
        self.retry = retry

    def load_config(self, force: bool = False):
        """Loads the deferred configuration."""
        if self._config is not None and (not self._config_loaded or force):
            self.init(**params_from_config(self._config))
            self._config_loaded = True

    def connect(self, *args, **kwargs) -> MySQLDatabase:
        """Initializes a database from the respective configuration."""
        self.load_config()
        return super().connect(*args, **kwargs)

    # pylint: disable=W0221
    def execute_sql(self, *args, retried: bool = False, **kwargs) -> Any:
        """Conditionally execute the SQL query in an
        execution context iff closing is enabled.
        """
        if self.connect_params.get('closing'):
            with self.connection_context():
                return super().execute_sql(*args, **kwargs)

        try:
            return super().execute_sql(*args, **kwargs)
        except OperationalError:
            if not self.connect_params.get('retry') or retried:
                raise

            if not self.is_closed():
                self.close()

            return self.execute_sql(*args, retried=True, **kwargs)
