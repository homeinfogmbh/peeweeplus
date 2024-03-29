"""Additional field definitions."""

from logging import getLogger

from peeweeplus.fields.char import BooleanCharField
from peeweeplus.fields.char import DecimalCharField
from peeweeplus.fields.char import DateTimeCharField
from peeweeplus.fields.char import DateCharField
from peeweeplus.fields.char import IntegerCharField
from peeweeplus.fields.char import RestrictedCharField
from peeweeplus.fields.datetime import TimedeltaField
from peeweeplus.fields.email import EMailField
from peeweeplus.fields.enum import EnumField
from peeweeplus.fields.html import HTMLCharField, HTMLTextField
from peeweeplus.fields.int import SmallUnsignedIntegerField
from peeweeplus.fields.int import UnsignedBigIntegerField
from peeweeplus.fields.int import UnsignedIntegerField
from peeweeplus.fields.ip import IPAddressField
from peeweeplus.fields.ip import IPv4AddressField
from peeweeplus.fields.ip import IPv6AddressField
from peeweeplus.fields.json import JSONTextField
from peeweeplus.fields.password import PasswordField
from peeweeplus.fields.phonenumber import PhoneNumberField
from peeweeplus.fields.username import UserNameField


__all__ = FIELDS = [
    "FIELDS",
    "BooleanCharField",
    "DateCharField",
    "DateTimeCharField",
    "DecimalCharField",
    "EMailField",
    "EnumField",
    "HTMLCharField",
    "HTMLTextField",
    "IntegerCharField",
    "IPAddressField",
    "IPv4AddressField",
    "IPv6AddressField",
    "JSONTextField",
    "PasswordField",
    "PhoneNumberField",
    "RestrictedCharField",
    "SmallUnsignedIntegerField",
    "TimedeltaField",
    "UnsignedBigIntegerField",
    "UnsignedIntegerField",
    "UserNameField",
]


LOGGER = getLogger(__file__)

try:
    from peeweeplus.fields.argon2 import Argon2Field
except ModuleNotFoundError as error:
    LOGGER.warning("Missing module: %s", error.name)
    LOGGER.warning("Argon2Field not available.")
else:
    __all__.append("Argon2Field")
