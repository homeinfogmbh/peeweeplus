"""JSON serialization."""

from base64 import b64encode
from contextlib import suppress
from typing import NamedTuple, Union

from peewee import BlobField
from peewee import DateField
from peewee import DateTimeField
from peewee import DecimalField
from peewee import Model
from peewee import TimeField
from peewee import UUIDField
from peeweeplus.fields import EnumField, IPv4AddressField
from peeweeplus.json.fields import get_json_fields, FieldConverter
from peeweeplus.json.filter import FieldsFilter


__all__ = ['serialize']


CONVERTER = FieldConverter({
    BlobField: b64encode,
    DecimalField: float,
    DateField: lambda value: value.isoformat(),
    DateTimeField: lambda value: value.isoformat(),
    EnumField: lambda value: value.value,
    IPv4AddressField: str,
    TimeField: lambda value: value.isoformat(),
    UUIDField: lambda value: value.hex
})


class Cascade(NamedTuple):
    """Represents cascading settings."""

    cascade: bool
    next: Union[bool, int]


def _check_cascade(cascade: Union[bool, int]) -> Cascade:
    """Returns a tuple of current cascade status
    and cascade status for the next level.
    """

    # If cascade is falsy, do not cascade now or in the next step.
    if not cascade:
        return Cascade(False, None)

    # If cascade is True, cascade down the whole tree.
    if isinstance(cascade, bool):
        return Cascade(True, True)

    # If it's an integer, count up or down to zero.
    # Zero itself ist matched by "if not cascade:…" from above.
    if isinstance(cascade, int):
        if cascade > 0:
            return Cascade(True, cascade - 1)

        return Cascade(True, cascade + 1)

    # On any other setting, do not cascade either.
    return Cascade(False, None)


def _get_model_value(model: Model, cascade: Union[bool, int],
                     null: bool = False, **filters) -> Union[dict, int]:
    """Converts a model to a JSON value."""

    cascade = _check_cascade(cascade)

    if cascade.cascade:
        with suppress(AttributeError):
            return model.to_json(null=null, cascade=cascade.next, **filters)

    return model.get_id()


def serialize(record: Model, *, null: bool = False,
              cascade: Union[bool, int] = None, **filters) -> dict:
    """Returns a JSON-ish dict with the record's fields' values."""

    model = type(record)
    fields = get_json_fields(model)
    fields_filter = FieldsFilter.for_serialization(**filters)
    json = {}

    for key, attribute, field in fields_filter.filter(fields):
        value = CONVERTER(field, getattr(record, attribute), check_null=False)

        if not null and value is None:
            continue

        if isinstance(value, Model):
            value = _get_model_value(value, cascade, null=null, **filters)

        json[key] = value

    return json
