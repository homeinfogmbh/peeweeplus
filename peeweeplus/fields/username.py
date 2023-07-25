"""Username field."""

from peeweeplus.fields.char import RestrictedCharField


__all__ = ["UserNameField"]


REGEX = r"^[0-9A-Za-zÄäÖöÜüßéè '-]+$"


class UserNameField(RestrictedCharField):
    """Restricted field to store email addresses."""

    def __init__(self, *args, **kwargs):
        super().__init__(REGEX, *args, **kwargs)
