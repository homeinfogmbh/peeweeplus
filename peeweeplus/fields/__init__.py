"""Additional field definitions."""

from logging import getLogger

from peeweeplus.fields.char import BooleanCharField
from peeweeplus.fields.char import IntegerCharField
from peeweeplus.fields.char import DecimalCharField
from peeweeplus.fields.char import DateTimeCharField
from peeweeplus.fields.char import DateCharField
from peeweeplus.fields.crypto import AESTextField
from peeweeplus.fields.enum import EnumField
from peeweeplus.fields.int import UnsignedBigIntegerField
from peeweeplus.fields.int import UnsignedIntegerField
from peeweeplus.fields.ip import IPAddressField
from peeweeplus.fields.ip import IPv4AddressField
from peeweeplus.fields.ip import IPv6AddressField
from peeweeplus.fields.json import JSONTextField
from peeweeplus.fields.password import PasswordField


__all__ = [
    'AESTextField',
    'BooleanCharField',
    'DateCharField',
    'DateTimeCharField',
    'DecimalCharField',
    'EnumField',
    'IntegerCharField',
    'IPAddressField',
    'IPv4AddressField',
    'IPv6AddressField',
    'JSONTextField',
    'PasswordField',
    'UnsignedBigIntegerField',
    'UnsignedIntegerField'
]


LOGGER = getLogger(__file__)

try:
    from peeweeplus.fields.argon2 import Argon2Field
except ModuleNotFoundError as error:
    LOGGER.error('Missing module: %s', error.name)
    LOGGER.warning('Argon2Field not available.')
else:
    __all__.append('Argon2Field')
