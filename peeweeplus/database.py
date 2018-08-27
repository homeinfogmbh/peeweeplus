"""Database enhancements."""

from peewee import OperationalError, MySQLDatabase as _MySQLDatabase

__all__ = ['MySQLDatabase']


class MySQLDatabase(_MySQLDatabase):
    """Extension of peewee.MySQLDatabase with closing option."""

    def __init__(self, *args, closing=False, retry=False, **kwargs):
        """Adds closing switch for automatic connection closing."""
        super().__init__(*args, **kwargs)
        self.closing = closing
        self.retry = retry

    @classmethod
    def from_config(cls, config):
        """Creates a database from the respective configuration."""
        try:
            database = config['db']
        except KeyError:
            database = config['database']

        try:
            passwd = config['passwd']
        except KeyError:
            passwd = config['password']

        closing = config.get('closing')
        retry = config.get('retry', True)

        return cls(
            database, host=config['host'], user=config['user'], passwd=passwd,
            closing=closing or False, retry=retry or False)

    def execute_sql(self, *args, retried=False, **kwargs):
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
