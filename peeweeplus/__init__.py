"""Practical extensions of the peewee ORM framework."""

from peeweeplus.contextmanagers import ChangedConnection
from peeweeplus.converters import dec2dom, dec2dict, dec2orm, date2orm, \
    datetime2orm
from peeweeplus.database import MySQLDatabase
from peeweeplus.exceptions import FieldValueError, FieldNotNullable, \
    MissingKeyError, InvalidKeys, NonUniqueValue, InvalidEnumerationValue, \
    PasswordTooShortError
from peeweeplus.fields import EnumField, CascadingFKField, Argon2Field, \
    IPv4AddressField
from peeweeplus.json import deserialize, serialize, JSONModel

__all__ = [
    'FieldValueError',
    'FieldNotNullable',
    'MissingKeyError',
    'InvalidKeys',
    'NonUniqueValue',
    'InvalidEnumerationValue',
    'PasswordTooShortError',
    'dec2dom',
    'dec2dict',
    'dec2orm',
    'date2orm',
    'datetime2orm',
    'deserialize',
    'serialize',
    'ChangedConnection',
    'MySQLDatabase',
    'JSONModel',
    'EnumField',
    'CascadingFKField',
    'Argon2Field',
    'IPv4AddressField']
