"""Database enhancements."""

from peewee import MySQLDatabase as _MySQLDatabase

__all__ = ['MySQLDatabase']


class MySQLDatabase(_MySQLDatabase):
    """Extension of peewee.MySQLDatabase with closing option."""

    def __init__(self, *args, closing=False, **kwargs):
        """Adds closing switch for automatic connection closing."""
        super().__init__(*args, **kwargs)
        self.closing = closing

    def execute_sql(self, sql, params=None, require_commit=True):
        """Conditionally execute the SQL query in an
        execution context iff closing is enabled.
        """
        if self.closing:
            with self.execution_context():
                return super().execute_sql(
                    sql, params=params, require_commit=require_commit)

        return super().execute_sql(
            sql, params=params, require_commit=require_commit)
