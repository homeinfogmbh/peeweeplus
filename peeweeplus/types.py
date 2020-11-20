"""Common types."""

from typing import Generator, Union

from peewee import Model


__all__ = ['JSON', 'ModelGenerator']


JSON = Union[bool, dict, float, int, list, None, str]
ModelGenerator = Generator[Model, None, None]
