"""User name field."""

from peeweeplus.fields.char import RestrictedCharField


__all__ = ['PhoneNumberField']


REGEX = r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$"


class PhoneNumberField(RestrictedCharField):
    """Restricted field to store email addresses."""

    def __init__(self, *args, **kwargs):
        super().__init__(REGEX, *args, **kwargs)
