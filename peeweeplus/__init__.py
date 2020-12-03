"""Practical extensions of the peewee ORM framework."""

from logging import getLogger

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
from peeweeplus.exceptions import PasswordTooShortError
from peeweeplus.fields import *
from peeweeplus.fields import __all__ as _ALL_FIELDS
from peeweeplus.json import JSON_FIELDS
from peeweeplus.json import deserialize
from peeweeplus.json import serialize
from peeweeplus.json import JSONMixin
from peeweeplus.json import JSONModel
from peeweeplus.transaction import Transaction


__all__ = [
    'JSON_FIELDS',
    'FieldValueError',
    'FieldNotNullable',
    'MissingKeyError',
    'InvalidKeys',
    'NonUniqueValue',
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
    'JSONMixin',
    'JSONModel',
    'Transaction'
] + _ALL_FIELDS


LOGGER = getLogger(__file__)


try:
    from peeweeplus.authlib import *
    from peeweeplus.authlib import __all__  as _ALL_AUTHLIB
except ModuleNotFoundError as error:
    LOGGER.warning('Missing module: %s', error.name)
    LOGGER.warning('Authlib integration not available.')
else:
    __all__ += _ALL_AUTHLIB
