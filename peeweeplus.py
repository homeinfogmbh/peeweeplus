"""peewee extensions for HOMEINFO"""

from base64 import b64encode
from contextlib import suppress
from json import dumps
from sys import stderr
from timelib import strpdatetime

import peewee

__all__ = [
    'create',
    'dec2dom',
    'dec2dict',
    'dec2orm',
    'date2orm',
    'datetime2orm',
    'MySQLDatabase',
    'JSONModel']


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


class JSONModel(peewee.Model):
    """A JSON-serializable model"""

    SHOW_PROTECTED = False
    DISPLAY_PK = False
    RECURSE_FK = False
    JSON_INDENT = None

    def __iter__(self):
        """Yields fields and values formatted for JSON complinace"""
        for attr in dir(self.__class__):
            if not attr.startswith('_') or self.SHOW_PROTECTED:
                field = getattr(self.__class__, attr)

                if isinstance(field, peewee.Field):
                    if isinstance(field, peewee.ForeignKeyField):
                        model = getattr(self, attr)

                        if model is not None:
                            if self.RECURSE_FK:
                                try:
                                    val = dict(model)
                                except (TypeError, ValueError):
                                    val = '<Not JSON serializable>'
                            else:
                                val = model._get_pk_value()
                        else:
                            val = model
                    elif isinstance(field, peewee.IntegerField):
                        if isinstance(field, peewee.PrimaryKeyField):
                            if not self.DISPLAY_PK:
                                continue

                        val = getattr(self, attr)
                    elif isinstance(field, peewee.DecimalField):
                        val = getattr(self, attr)

                        if val is not None:
                            val = float(val)
                    elif isinstance(field, peewee.FloatField):
                        val = getattr(self, attr)
                    elif isinstance(field, peewee.CharField):
                        val = getattr(self, attr)
                    elif isinstance(field, peewee.TextField):
                        val = getattr(self, attr)
                    elif isinstance(field, peewee.DateTimeField):
                        val = getattr(self, attr)

                        if val is not None:
                            val = val.isoformat()
                    elif isinstance(field, peewee.DateField):
                        val = getattr(self, attr)

                        if val is not None:
                            val = val.isoformat()
                    elif isinstance(field, peewee.TimeField):
                        val = getattr(self, attr)

                        if val is not None:
                            val = val.isoformat()
                    elif isinstance(field, peewee.BooleanField):
                        val = getattr(self, attr)
                    elif isinstance(field, peewee.BlobField):
                        val = getattr(self, attr)

                        if val is not None:
                            val = b64encode(val)
                    else:
                        print('Unknown Field type: {}'.format(field),
                              file=stderr)
                        continue

                    yield (attr, val)

    def __str__(self):
        """Returns the model as a JSON string"""
        return dumps(dict(self), indent=self.JSON_INDENT)
