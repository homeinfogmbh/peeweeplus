"""Password based encryption and decryption."""

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random


__all__ = ['encrypt', 'decrypt']


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
