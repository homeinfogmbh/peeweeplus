"""peewee extensions for HOMEINFO"""

from contextlib import suppress
from datetime import strpdatetime

import peewee

__all__ = [
    'create',
    'dec2dom',
    'dec2dict',
    'dec2orm',
    'date2orm',
    'datetime2orm',
    'MySQLDatabase']


def create(model):
    """Decorator for peewee.Model definitions that
    actually should be created on load.

    Usage:
        @create
        class MyModel(peewee.Model):
            pass
    """

    with suppress(peewee.OperationalError):
        with model._meta.database.execution_context():
            model.create_table(fail_silently=True)

    return model


def dec2dom(value):
    """Converts decimal values into DOM-compatible strings"""

    if value is not None:
        return str(value)


def dec2dict(value):
    """Converts decimal values into DOM-compatible strings"""

    if value is not None:
        return float(value)


def dec2orm(value):
    """Converts decimal values into ORM-compatible floats"""

    if value is not None:
        return float(value)


def date2orm(value):
    """Converts a PyXB date object to a datetime.date object"""

    if value is not None:
        return value.date()


def datetime2orm(value):
    """Converts a PyXB date object to a datetime.date object"""

    if value is not None:
        return strpdatetime(value.isoformat())


class MySQLDatabase(peewee.MySQLDatabase):
    """Extension of peewee.MySQLDatabase with closing option"""

    def __init__(self, *args, closing=False, **kwargs):
        """Adds closing switch for automatic connection closing"""
        super().__init__(*args, **kwargs)
        self.closing = closing

    def execute_sql(self, *args, **kwargs):
        """Conditionally execute the SQL query in an
        execution context iff closing is enabled
        """
        if self.closing:
            with self.execution_context():
                return super().execute_sql(*args, **kwargs)
        else:
            return super().execute_sql(*args, **kwargs)
