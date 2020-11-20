"""JSON serialization."""

from base64 import b64encode
from contextlib import suppress
from typing import Tuple, Union

from peewee import BlobField
from peewee import DateField
from peewee import DateTimeField
from peewee import DecimalField
from peewee import ForeignKeyField
from peewee import Model
from peewee import TimeField
from peewee import UUIDField
from peeweeplus.fields import EnumField, IPv4AddressField
from peeweeplus.json.fields import get_json_fields, FieldConverter
from peeweeplus.json.filter import FieldsFilter
from peeweeplus.json.parsers import get_fk_value


__all__ = ['serialize']


CONVERTER = FieldConverter({
    BlobField: b64encode,
    DecimalField: float,
    DateField: lambda value: value.isoformat(),
    DateTimeField: lambda value: value.isoformat(),
    EnumField: lambda value: value.value,
    ForeignKeyField: get_fk_value,
    IPv4AddressField: str,
    TimeField: lambda value: value.isoformat(),
    UUIDField: lambda value: value.hex
})


def _check_cascade(key: str, attribute: str,
                   cascade: Union[bool, int]) -> Tuple[bool, bool]:
    """Returns a tuple of current cascade status
    and cascade status for the next level.
    """

    # If cascade is falsy, do not cascade now or in the next step.
    if not cascade:
        return (False, None)

    # If cascade is True, cascade down the whole tree.
    if isinstance(cascade, bool):
        return (True, True)

    # If it's an integer, count up or down to zero.
    # Zero itself ist matched by "if not cascade:…" from above.
    if isinstance(cascade, int):
        return (True, cascade - 1) if cascade > 0 else (True, cascade + 1)

    # If it's a dict, get the next cascade
    # setting from the field key or attribute.
    if isinstance(cascade, dict):
        with suppress(KeyError):
            return (True, cascade[key])

        with suppress(KeyError):
            return (True, cascade[attribute])

    # On any other setting, do not cascade either.
    return (False, None)


def serialize(record: Model, *, null: bool = False,
              cascade: Union[bool, int] = None, **filters) -> dict:
    """Returns a JSON-ish dict with the record's fields' values."""

    model = type(record)
    fields = get_json_fields(model)
    fields_filter = FieldsFilter.for_serialization(**filters)
    json = {}

    for key, attribute, field in fields_filter.filter(fields):
        value = getattr(record, attribute)
        value = CONVERTER(field, value, check_null=False)
        do_cascade, cascade_next = _check_cascade(key, attribute, cascade)

        if do_cascade and isinstance(field, ForeignKeyField):
            with suppress(field.rel_model.DoesNotExist, AttributeError):
                value = field.rel_model[value].to_json(
                    null=null, cascade=cascade_next, **filters)

        if not null and value is None:
            continue

        json[key] = value

    return json
