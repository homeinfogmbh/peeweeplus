"""Enum field accessor."""

from peewee import FieldAccessor

from peeweeplus.exceptions import InvalidEnumerationValue


__all__ = ['EnumFieldAccessor']


class EnumFieldAccessor(FieldAccessor):
    """Accessor class for EnumField."""

    def __set__(self, instance, value):
        """Sets the respective enumeration."""
        if value is not None:
            try:
                value = self.field.enum(value)
            except ValueError:
                raise InvalidEnumerationValue(value, self.field.enum)

        super().__set__(instance, value)
