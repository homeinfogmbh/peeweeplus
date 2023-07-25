"""Miscellaneous stuff."""

from functools import cache
from typing import Any, Iterable, Iterator, NamedTuple, Type

from peewee import Field, ForeignKeyField, Model

from peeweeplus.exceptions import NullError


__all__ = [
    "JSONField",
    "FieldConverter",
    "contains",
    "get_json_fields",
]


class JSONField(NamedTuple):
    """JSON field information tuple."""

    key: str
    attribute: str
    field: Field


class FieldConverter(dict):
    """Maps conversion functions to field classes."""

    def __call__(self, field: Field, value: Any, check_null: bool = False) -> Any:
        """Converts the respective value to the field."""

        if value is None:
            if check_null and not field.null:
                raise NullError()

            return None

        for typ, function in self.items():
            if isinstance(field, typ):
                break
        else:
            return value

        try:
            return function(value)
        except TypeError:
            return function(value, field)


def contains(
    iterable: Iterable, key: str, attribute: str, *, default: bool = False
) -> bool:
    """Determines whether the field is contained within the iterable."""

    if iterable:
        return key in iterable or attribute in iterable

    return default


@cache
def get_json_fields(model: Type[Model]) -> frozenset[JSONField]:
    """Returns the JSON fields of the respective model
    and caches it in the JSON_FIELDS dict.
    """

    return frozenset(_get_json_fields(model))


def _get_json_fields(model: Type[Model]) -> Iterator[JSONField]:
    """Yields the JSON fields of the respective model."""

    fields = model._meta.fields

    try:
        key_formatter = model.__key_formatter__
    except AttributeError:
        key_formatter = None

    for attribute, field in fields.items():
        if attribute.startswith("_"):
            continue

        if isinstance(field, ForeignKeyField):
            if attribute.endswith("_id") and attribute + "_id" not in fields:
                continue

        if key_formatter is not None:
            key = key_formatter(field.column_name)
        else:
            key = field.column_name

        yield JSONField(key, field.name, field)
