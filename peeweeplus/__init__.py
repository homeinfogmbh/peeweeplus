"""Practical extensions of the peewee ORM framework."""

from logging import getLogger

from peeweeplus.contextmanagers import ChangedConnection
from peeweeplus.converters import dec2dom
from peeweeplus.converters import dec2dict
from peeweeplus.converters import dec2orm
from peeweeplus.converters import date2orm
from peeweeplus.converters import datetime2orm
from peeweeplus.database import MySQLDatabase
from peeweeplus.dbproxy import DatabaseProxy, MySQLDatabaseProxy
from peeweeplus.exceptions import FieldValueError
from peeweeplus.exceptions import FieldNotNullable
from peeweeplus.exceptions import MissingKeyError
from peeweeplus.exceptions import InvalidKeys
from peeweeplus.exceptions import NonUniqueValue
from peeweeplus.exceptions import PasswordTooShort
from peeweeplus.fields import *
from peeweeplus.fields import FIELDS
from peeweeplus.json import JSON_FIELDS
from peeweeplus.json import deserialize
from peeweeplus.json import serialize
from peeweeplus.json import JSONMixin
from peeweeplus.json import JSONModel
from peeweeplus.mixins import FileMixin
from peeweeplus.model import select_tree
from peeweeplus.transaction import Transaction


__all__ = [
    'JSON_FIELDS',
    'FieldValueError',
    'FieldNotNullable',
    'MissingKeyError',
    'InvalidKeys',
    'NonUniqueValue',
    'PasswordTooShort',
    'dec2dom',
    'dec2dict',
    'dec2orm',
    'date2orm',
    'datetime2orm',
    'deserialize',
    'select_tree',
    'serialize',
    'ChangedConnection',
    'DatabaseProxy',
    'FileMixin',
    'MySQLDatabase',
    'MySQLDatabaseProxy',
    'JSONMixin',
    'JSONModel',
    'Transaction'
] + FIELDS


LOGGER = getLogger(__file__)
