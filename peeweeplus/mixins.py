"""Model mixins."""

from __future__ import annotations
from hashlib import sha256
from mimetypes import guess_extension
from typing import Iterator

from magic import detect_from_content
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
        return cls(
            bytes=data,
            size=len(data),
            sha256sum=sha256(data).hexdigest(),
            mimetype=(mimetype := detect_from_content(data[:1024])),
            suffix=guess_extension(mimetype)
        )

    @classmethod
    def shallow(cls) -> Iterator[Field]:
        """Yields all fields except BlobFields."""
        return filter(lambda field: not isinstance(field, BlobField),
                      cls._meta.fields.values())
