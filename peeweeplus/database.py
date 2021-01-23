"""Database enhancements."""

from __future__ import annotations
from configparser import SectionProxy
from typing import Any, Union

from peewee import OperationalError, MySQLDatabase


__all__ = ['MySQLDatabase']


def params_from_config(config: Union[SectionProxy, dict]) -> dict:
    """Returns the database params from the configuration."""

    return {
        'database': config.get('db', config.get('database')),
        'passwd': config.get('passwd', config.get('password')),
        'closing': config.getboolean('closing', True),
        'retry': config.getboolean('retry', False)
    }


class MySQLDatabase(MySQLDatabase):     # pylint: disable=E0102,W0223
    """Extension of peewee.MySQLDatabase with closing option."""

    @classmethod
    def from_config(cls, config: Union[SectionProxy, dict]) -> MySQLDatabase:
        """Creates a database from the respective configuration."""
        return cls(**params_from_config(config))

    def load_config(self, config: Union[SectionProxy, dict]) -> MySQLDatabase:
        """Initializes a database from the respective configuration."""
        return self.init(**params_from_config(config))

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
