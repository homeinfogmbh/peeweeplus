"""IP-related fields."""

from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Optional, Union

from peewee import CharField, Field

from peeweeplus.fields.int import UnsignedIntegerField


__all__ = ["IPAddressField", "IPv4AddressField", "IPv6AddressField"]


IPAddress = Union[IPv4Address, IPv6Address]


class IPAddressField(CharField):
    """Field to store IPv4 or IPv6 addresses as strings."""

    def __init__(self, *args, max_length: int = 45, **kwargs):
        """Defaults the max_length to 45 according to:
        https://stackoverflow.com/a/7477384/3515670
        """
        super().__init__(*args, max_length=max_length, **kwargs)

    def db_value(self, value: Optional[IPAddress]) -> Optional[str]:
        """Returns the IP address' string value or None."""
        if value is None:
            return None

        return str(value)

    def python_value(self, value: Optional[str]) -> Optional[IPAddress]:
        """Returns the IP address object or None."""
        if value is None:
            return None

        return ip_address(value)


class IPv4AddressField(UnsignedIntegerField):
    """Field to store IPv4 addresses as integers."""

    def db_value(self, value: Optional[IPv4Address]) -> Optional[int]:
        """Returns the IPv4 address's integer value or None."""
        if value is None:
            return None

        return int(value)

    def python_value(self, value: Optional[int]) -> Optional[IPv4Address]:
        """Returns the IPv4 address object or None."""
        if value is None:
            return None

        return IPv4Address(value)


class IPv6AddressField(Field):
    """Field to store IPv4 or IPv6 addresses as integers."""

    field_type = "BINARY(16)"

    def db_value(self, value: Optional[IPv6Address]) -> Optional[bytes]:
        """Returns the IPv4 address's integer value or None."""
        if value is None:
            return None

        return int(value).to_bytes(16, "big")

    def python_value(self, value: Optional[bytes]) -> Optional[IPv6Address]:
        """Returns the IP address object or None."""
        if value is None:
            return None

        return IPv6Address(value)
