"""Additional field definitions."""

from logging import getLogger

from peeweeplus.exceptions import MissingModule
from peeweeplus.fields.char import BooleanCharField
from peeweeplus.fields.char import IntegerCharField
from peeweeplus.fields.char import DecimalCharField
from peeweeplus.fields.char import DateTimeCharField
from peeweeplus.fields.char import DateCharField
from peeweeplus.fields.common import PasswordField
from peeweeplus.fields.crypto import AESTextField
from peeweeplus.fields.enum import EnumField
from peeweeplus.fields.int import UnsignedIntegerField
from peeweeplus.fields.ip import IPv4AddressField
from peeweeplus.fields.json import JSONTextField


__all__ = [
    'AESTextField',
    'BooleanCharField',
    'DateCharField',
    'DateTimeCharField',
    'DecimalCharField',
    'EnumField',
    'IntegerCharField',
    'IPv4AddressField',
    'JSONTextField',
    'PasswordField',
    'UnsignedIntegerField'
]


LOGGER = getLogger(__file__)

try:
    from peeweeplus.fields.argon2 import Argon2Field
except MissingModule as error:
    LOGGER.warning('Missing module "%s".', error.module)
    LOGGER.warning('Argon2Field not available.')
else:
    __all__.append('Argon2Field')
