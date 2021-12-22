"""Model mixins."""

from __future__ import annotations
from typing import Iterator

from mimeutil import FileMetaData
from peewee import BlobField
from peewee import CharField
from peewee import Field
from peewee import FixedCharField
from peewee import IntegerField


__all__ = ['FileMixin']


class FileMixin:
    """Mixin for binary data."""

    bytes = BlobField()
    size = IntegerField()
    sha256sum = FixedCharField(64)
    mimetype = CharField()
    suffix = CharField()

    @classmethod
    def from_bytes(cls, data: bytes) -> FileMixin:
        """Creates a file from the given bytes."""
        return cls(bytes=data, size=len(data), **FileMetaData.from_bytes(data))

    @classmethod
    def shallow(cls) -> Iterator[Field]:
        """Yields all fields except BlobFields."""
        return filter(lambda field: not isinstance(field, BlobField),
                      cls._meta.fields.values())
