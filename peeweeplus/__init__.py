"""Practical extensions of the peewee ORM framework."""

from peeweeplus.contextmanagers import ChangedConnection
from peeweeplus.converters import dec2dom, dec2dict, dec2orm, date2orm, \
    datetime2orm
from peeweeplus.database import MySQLDatabase
from peeweeplus.exceptions import FieldValueError, FieldNotNullable, \
    MissingKeyError, InvalidKeys, InvalidEnumerationValue, \
    PasswordTooShortError
from peeweeplus.fields import EnumField, CascadingFKField, UUID4Field, \
    Argon2Field
from peeweeplus.json import iterfields, deserialize, serialize, JSONModel

__all__ = [
    'FieldValueError',
    'FieldNotNullable',
    'MissingKeyError',
    'InvalidKeys',
    'InvalidEnumerationValue',
    'PasswordTooShortError',
    'dec2dom',
    'dec2dict',
    'dec2orm',
    'date2orm',
    'datetime2orm',
    'iterfields',
    'deserialize',
    'serialize',
    'ChangedConnection',
    'MySQLDatabase',
    'JSONModel',
    'EnumField',
    'CascadingFKField',
    'UUID4Field',
    'Argon2Field']
