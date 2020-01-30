"""Cryptographic fields."""

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

from peewee import FieldAccessor, TextField


__all__ = ['encrypt', 'decrypt', 'AESTextFieldAccessor', 'AESTextField']


def password_to_key(password):
    """Use SHA-256 over our password to get a proper-sized AES key."""

    return SHA256.new(password).digest()


def encrypt(source, key):
    """Encrypts the text with the given key."""

    key = password_to_key(key)
    # Generate initialization vector.
    i_v = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_GCM, i_v)
    # Calculate needed padding.
    padding = AES.block_size - len(source) % AES.block_size
    source += bytes([padding]) * padding
    # Store the IV at the beginning and encrypt.
    return i_v + encryptor.encrypt(source)


def decrypt(source, key):
    """Decrypts the cipher text with the given key."""

    key = password_to_key(key)
    # Extract the initialization vector from the beginning.
    i_v = source[:AES.block_size]
    decryptor = AES.new(key, AES.MODE_GCM, i_v)
    data = decryptor.decrypt(source[AES.block_size:])
    padding = data[-1]

    if data[-padding:] != bytes([padding]) * padding:
        raise ValueError("Invalid padding...")

    return data[:-padding]


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
