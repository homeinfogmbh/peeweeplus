"""Common types."""

from typing import Union


__all__ = ["JSON"]


JSON = Union[bool, dict, float, int, list, None, str]
