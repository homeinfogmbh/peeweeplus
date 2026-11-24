"""JSON serialization."""

from base64 import b64encode
from contextlib import suppress
from functools import lru_cache
from typing import Any, Callable, NamedTuple, Optional, Type, Union

from peewee import BlobField
from peewee import DateField
from peewee import DateTimeField
from peewee import DecimalField
from peewee import Field
from peewee import Model
from peewee import TimeField
from peewee import UUIDField
from peeweeplus.fields import EnumField, IPv4AddressField, IPv6AddressField
from peeweeplus.json.fields import convert, get_json_fields, FieldConverter
from peeweeplus.json.filter import FieldsFilter


__all__ = ["serialize"]


CONVERTER = FieldConverter(
    {
        BlobField: b64encode,
        DecimalField: float,
        DateField: lambda value: value.isoformat(),
        DateTimeField: lambda value: value.isoformat(),
        EnumField: lambda value: value.value,
        IPv4AddressField: str,
        IPv6AddressField: str,
        TimeField: lambda value: value.isoformat(),
        UUIDField: lambda value: value.hex,
    }
)


class FieldSerializer(NamedTuple):
    """A field to be serialized and its conversion function."""

    key: str
    attribute: str
    field: Field
    function: Optional[Callable[..., Any]]


@lru_cache(maxsize=1024)
def get_serializers(
    model: Type[Model], fields_filter: FieldsFilter
) -> tuple[FieldSerializer, ...]:
    """Returns the fields of the model that pass the filter with their
    conversion functions.

    Filtering the fields and looking up the functions for each record takes
    longer than the conversion itself, but depends on the model only.
    """

    return tuple(
        FieldSerializer(key, attribute, field, CONVERTER.get_function(field))
        for key, attribute, field in fields_filter.filter(get_json_fields(model))
    )


def _next(cascade: Union[bool, int]) -> Union[bool, int]:
    """Returns the next cascading step."""

    if not cascade:
        return False

    if cascade is True:
        return True

    if cascade > 0:
        return cascade - 1

    return cascade + 1


def _get_model_value(
    model: Model, cascade: Union[bool, int], null: bool = False, **filters
) -> Union[dict, int]:
    """Converts a model to a JSON value."""

    if cascade:
        with suppress(AttributeError):
            return model.to_json(null=null, cascade=_next(cascade), **filters)

    return model.get_id()


def serialize(
    record: Model, *, null: bool = False, cascade: Union[bool, int] = None, **filters
) -> dict:
    """Returns a JSON-ish dict with the record's fields' values."""

    fields_filter = FieldsFilter.for_serialization(**filters)
    json = {}

    for key, attribute, field, function in get_serializers(type(record), fields_filter):
        value = getattr(record, attribute)

        if value is not None and function is not None:
            value = convert(function, value, field)

        if not null and value is None:
            continue

        if isinstance(value, Model):
            value = _get_model_value(value, cascade, null=null, **filters)

        json[key] = value

    return json
