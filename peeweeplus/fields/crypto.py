"""Cryptographic fields."""

from base64 import b64encode, b64decode

from peewee import FieldAccessor, TextField

from peeweeplus.crypto import encrypt, decrypt


__all__ = ['AESTextFieldAccessor', 'AESTextField']


class AESTextFieldAccessor(FieldAccessor):  # pylint: disable=R0903
    """Accessor class for AESTextField."""

    def __get__(self, instance, instance_type=None):
        """Gets the value."""
        if instance is None:
            return super().__get__(instance, instance_type=instance_type)

        value = instance.__data__.get(self.name)

        if value is None:
            return value

        value = value.encode()
        value = b64decode(value)
        value = decrypt(value, self.field.key)
        value = value.decode(self.field.encoding)
        return value

    def __set__(self, instance, value):
        """Sets the password hash."""
        if value is not None:
            value = value.encode(self.field.encoding)
            value = encrypt(value, self.field.key)
            value = b64encode(value)
            value = value.decode()

        super().__set__(instance, value)


class AESTextField(TextField):
    """Stores AES encrypted text."""

    accessor_class = AESTextFieldAccessor

    def __init__(self, *args, encoding='utf-8', key=None, **kwargs):
        """Sets the encoding and key."""
        super().__init__(*args, **kwargs)
        self.encoding = encoding

        if key is None:
            raise ValueError('No key specified.')

        self.key = key
