"""IP-related fields."""

from ipaddress import IPv4Address

from peeweeplus.fields.int import UnsignedIntegerField


__all__ = ['IPv4AddressField']


class IPv4AddressField(UnsignedIntegerField):
    """Field to store IPv4 addresses."""

    def db_value(self, value):  # pylint: disable=R0201
        """Returns the IPv4 address's interger value or None."""
        if value is None:
            return None

        return int(value)

    def python_value(self, value):  # pylint: disable=R0201
        """Returns the IPv4 address object or None."""
        if value is None:
            return None

        return IPv4Address(value)
