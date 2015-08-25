"""peewee extensions for HOMEINFO"""

from peewee import MySQLDatabase as PeeweeMySQLDatabase, OperationalError
from contextlib import suppress


def create(model):
    """Decorator for peewee.Model definitions that
    actually should be created on load.

    Usage:
        @create
        class MyModel(peewee.Model):
            pass
    """
    with suppress(OperationalError):
        with model._meta.database.execution_context():
            model.create_table(fail_silently=True)
    return model


class MySQLDatabase(PeeweeMySQLDatabase):
    """Extension of peewee.MySQLDatabase with closing option"""

    def __init__(self, *args, closing=False, **kwargs):
        """Adds closing switch for automatic connection closing"""
        super().__init__(*args, **kwargs)
        self.closing = closing

    def execute_sql(self, *args, **kwargs):
        if self.closing:
            with self.execution_context():
                return super().execute_sql(*args, **kwargs)
        else:
            return super().execute_sql(*args, **kwargs)
