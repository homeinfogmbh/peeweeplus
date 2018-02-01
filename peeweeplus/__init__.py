"""Practical extensions of the peewee ORM framework."""

from peewee import Field

from peeweeplus.converters import dec2dom, dec2dict, dec2orm, date2orm, \
    datetime2orm
from peeweeplus.database import MySQLDatabase
from peeweeplus.fields import InvalidEnumerationValue, EnumField
from peeweeplus.json import FieldValueError, FieldNotNullable, iterfields, \
    deserialize, serialize, JSONModel

__all__ = [
    'FieldValueError',
    'FieldNotNullable',
    'InvalidEnumerationValue',
    'dec2dom',
    'dec2dict',
    'dec2orm',
    'date2orm',
    'datetime2orm',
    'deserialize',
    'serialize',
    'MySQLDatabase',
    'JSONModel',
    'EnumField']


# Quick fix.
def _get_db_column(self):
    return self.column_name


def _set_db_column(self, db_column):
    self.column_name = db_column


Field.db_column = property(_get_db_column, _set_db_column)
