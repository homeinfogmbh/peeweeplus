"""Practical extensions of the peewee ORM framework."""

from peeweeplus.contextmanagers import ChangedConnection
from peeweeplus.converters import dec2dom
from peeweeplus.converters import dec2dict
from peeweeplus.converters import dec2orm
from peeweeplus.converters import date2orm
from peeweeplus.converters import datetime2orm
from peeweeplus.database import MySQLDatabase
from peeweeplus.exceptions import FieldValueError
from peeweeplus.exceptions import FieldNotNullable
from peeweeplus.exceptions import MissingKeyError
from peeweeplus.exceptions import InvalidKeys
from peeweeplus.exceptions import NonUniqueValue
from peeweeplus.exceptions import InvalidEnumerationValue
from peeweeplus.exceptions import PasswordTooShortError
from peeweeplus.fields import EnumField
from peeweeplus.fields import CascadingFKField
from peeweeplus.fields import Argon2Field
from peeweeplus.fields import IPv4AddressField
from peeweeplus.json import deserialize, serialize, JSONMixin, JSONModel
from peeweeplus.query import async_query


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
    'async_query',
    'ChangedConnection',
    'MySQLDatabase',
    'JSONMixin',
    'JSONModel',
    'EnumField',
    'CascadingFKField',
    'Argon2Field',
    'IPv4AddressField']
