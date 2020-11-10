"""IP-related fields."""

from ipaddress import IPv4Address, IPv6Address, ip_address

from peewee import CharField

from peeweeplus.fields.int import UnsignedIntegerField, UnsignedBigIntegerField


__all__ = ['IPAddressField', 'IPv4AddressField', 'IPv6AddressField']


class IPAddressField(CharField):
    """Field to store IPv4 or IPv6 addresses as strings."""

    def __init__(self, *args, **kwargs):
        """Sets the max_length to 39 chars for hex representation of IPv6."""
        super().__init__(*args, max_length=39, **kwargs)

    def db_value(self, value):  # pylint: disable=R0201
        """Returns the IP address' string value or None."""
        if value is None:
            return None

        return str(value)

    def python_value(self, value):  # pylint: disable=R0201
        """Returns the IP address object or None."""
        if value is None:
            return None

        return ip_address(value)


class IPv4AddressField(UnsignedIntegerField):
    """Field to store IPv4 addresses as integers."""

    def db_value(self, value):  # pylint: disable=R0201
        """Returns the IPv4 address's integer value or None."""
        if value is None:
            return None

        return int(value)

    def python_value(self, value):  # pylint: disable=R0201
        """Returns the IPv4 address object or None."""
        if value is None:
            return None

        return IPv4Address(value)


class IPv6AddressField(UnsignedBigIntegerField):
    """Field to store IPv4 or IPv6 addresses as integers."""

    def db_value(self, value):  # pylint: disable=R0201
        """Returns the IPv4 address's integer value or None."""
        if value is None:
            return None

        return int(value)

    def python_value(self, value):  # pylint: disable=R0201
        """Returns the IP address object or None."""
        if value is None:
            return None

        return IPv6Address(value)
