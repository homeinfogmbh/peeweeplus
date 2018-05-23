"""Database enhancements."""

from peewee import MySQLDatabase as _MySQLDatabase

__all__ = ['MySQLDatabase']


class MySQLDatabase(_MySQLDatabase):
    """Extension of peewee.MySQLDatabase with closing option."""

    def __init__(self, *args, closing=False, **kwargs):
        """Adds closing switch for automatic connection closing."""
        super().__init__(*args, **kwargs)
        self.closing = closing

    @classmethod
    def from_config(cls, config, closing=True):
        """Creates a database from the respective configuration."""
        return cls(
            config['db'], host=config['host'], user=config['user'],
            passwd=config['passwd'], closing=config.get('closing', closing))

    def execute_sql(self, *args, **kwargs):
        """Conditionally execute the SQL query in an
        execution context iff closing is enabled.
        """
        if self.closing:
            with self.connection_context():
                return super().execute_sql(*args, **kwargs)

        return super().execute_sql(*args, **kwargs)
