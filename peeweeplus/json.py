"""JSON serialization and deserialization."""

from base64 import b64decode, b64encode
from contextlib import suppress
from datetime import datetime, date, time
from functools import lru_cache

from peewee import Model, Field, PrimaryKeyField, ForeignKeyField, \
    BooleanField, IntegerField, FloatField, DecimalField, DateTimeField, \
    DateField, TimeField, BlobField

from timelib import strpdatetime, strpdate, strptime

from peeweeplus.fields import EnumField

__all__ = [
    'FieldValueError',
    'FieldNotNullable',
    'InvalidKeys',
    'iterfields',
    'fieldtuple',
    'deserialize',
    'serialize',
    'JSONModel']


class NullError(TypeError):
    """Indicates that the respective field cannot be null."""

    pass


class FieldValueError(ValueError):
    """Indicates that the field cannot store data of the provided type."""

    def __init__(self, model, attr, field, value):
        """Sets the field and value."""
        super().__init__(model, attr, field, value)
        self.model = model
        self.attr = attr
        self.field = field
        self.value = value

    def __str__(self):
        """Returns the respective error message."""
        return (
            '<{field.__class__.__name__} {field.column_name}> at <{model.'
            '__class__.__name__}.{attr}> cannot store {typ}: {value}.').format(
                field=self.field, model=self.model, attr=self.attr,
                typ=type(self.value), value=self.value)

    def to_dict(self):
        """Returns a JSON-ish representation of this error."""
        return {
            'model': self.model.__name__,
            'attr': self.attr,
            'field': self.field.__class__.__name__,
            'column_name': self.field.column_name,
            'value': str(self.value),
            'type': str(type(self.value))}


class FieldNotNullable(FieldValueError):
    """Indicates that the field was assigned
    a NULL value which it cannot store.
    """

    def __init__(self, model, attr, field):
        """Sets the field."""
        super().__init__(model, attr, field, None)

    def __str__(self):
        """Returns the respective error message."""
        return (
            '<{field.__class__.__name__} {field.column_name}> at '
            '<{model.__class__.__name__}.{attr}> must not be NULL.').format(
                field=self.field, model=self.model, attr=self.attr)


class InvalidKeys(ValueError):
    """Indicates that the respective keys can not be consumed by the model."""

    def __init__(self, invalid_keys):
        """Sets the respective invalid keys."""
        super().__init__(invalid_keys)
        self.invalid_keys = invalid_keys

    def __iter__(self):
        """Yields the invalid keys."""
        yield from self.invalid_keys


def _issubclass(cls, classes):
    """Safe subclass check."""

    try:
        return issubclass(cls, classes)
    except TypeError:
        return False


def iterfields(model, primary_key=True):
    """Yields JSON-key, attribute name and field
    instance for each field  of the model.
    """

    if primary_key:
        invalid_fields = ForeignKeyField
    else:
        invalid_fields = (PrimaryKeyField, ForeignKeyField)

    for name, field in model._meta.fields.items():
        if not name.startswith('_') and not isinstance(field, invalid_fields):
            yield (field.column_name, name, field)


@lru_cache()
def fieldtuple(model, primary_key=True):
    """Returns a set of the model's respective fields."""

    return tuple(iterfields(model, primary_key=primary_key))


def field_to_json(field, value):
    """Converts the given field's value into JSON-ish data."""

    if value is None:
        return None
    elif isinstance(field, DecimalField):
        return float(value)
    elif isinstance(field, (DateTimeField, DateField, TimeField)):
        return value.isoformat()
    elif isinstance(field, BlobField):
        return b64encode(value)
    elif isinstance(field, EnumField):
        return value.value

    return value


def value_to_field(value, field):
    """Converts a value for the provided field."""

    if value is None:
        if not field.null:
            raise NullError()

        return None
    elif isinstance(field, BooleanField):
        if isinstance(value, (bool, int)):
            return bool(value)

        raise ValueError(value)
    elif isinstance(field, IntegerField):
        return int(value)
    elif isinstance(field, FloatField):
        return float(value)
    elif isinstance(field, DecimalField):
        return float(value)
    elif isinstance(field, DateTimeField):
        if isinstance(value, datetime):
            return value

        return strpdatetime(value)
    elif isinstance(field, DateField):
        if isinstance(value, date):
            return value

        return strpdate(value)
    elif isinstance(field, TimeField):
        if isinstance(value, time):
            return value

        return strptime(value)
    elif isinstance(field, BlobField):
        if isinstance(value, bytes):
            return value

        return b64decode(value)

    return value


def deserialize(target, dictionary, *, strict=True, allow=()):
    """Applies the provided dictionary onto the target.
    The target can either be a Model subclass (deserialization)
    or a Model instance (patching).
    """

    if isinstance(target, Model):
        model = target.__class__
        patch = True
    elif issubclass(target, Model):
        model = target
        patch = False
    else:
        raise TypeError('Cannot apply dictionary to: {}.'.format(target))

    json_fields = fieldtuple(model, primary_key=False)
    allowed_keys = {key for key, *_ in json_fields}
    allowed_keys.update(allow)
    invalid_keys = set(key for key in dictionary if key not in allowed_keys)

    if invalid_keys and strict:
        raise InvalidKeys(invalid_keys)

    record = target if patch else model()

    for key, attribute, field in json_fields:
        try:
            value = dictionary[key]
        except KeyError:
            if not patch and field.default is None and not field.null:
                raise FieldNotNullable(model, attribute, field)

            continue

        try:
            field_value = value_to_field(value, field)
        except NullError:
            raise FieldNotNullable(model, attribute, field)
        except (TypeError, ValueError):
            raise FieldValueError(model, attribute, field, value)

        setattr(record, attribute, field_value)

    return record


def _dict_items_gen(record, fields, only, ignore, null):
    """Yields the respective dictionary items."""

    for key, attribute, field in fields:
        if only is not None and (key, attribute, field) not in only:
            continue

        if ignore is not None and (key, attribute, field) in ignore:
            continue

        value = getattr(record, attribute)

        if value is not None or null:
            yield (key, field_to_json(field, value))


@lru_cache()
def _dict_items_tuple(record, fields, only, ignore, null):
    """Returns the respective set of dictionary items."""

    return tuple(_dict_items_gen(record, fields, only, ignore, null))


def serialize(record, *, only=None, ignore=None, null=False, primary_key=True):
    """Returns a JSON-ish dictionary with the record's values."""

    if only is not None:
        only = FieldList(only)

    if ignore is not None:
        ignore = FieldList(ignore)

    json_fields = fieldtuple(record.__class__, primary_key=primary_key)
    return dict(_dict_items_tuple(record, json_fields, only, ignore, null))


class FieldList:
    """A list of DB columns, attributes or fields."""

    def __init__(self, items):
        """Splits into a list of strings and fields."""
        self.strings = set()
        fields = []
        field_types = []

        for item in items:
            if isinstance(item, Field):
                fields.append(item.__class__)
                continue

            with suppress(TypeError):
                if issubclass(item, Field):
                    field_types.append(item)
                    continue

            self.strings.add(item)

        self.fields = tuple(fields)             # Need tuple for isinstance().
        self.field_types = tuple(field_types)   # Need tuple for issubclass().

    def __contains__(self, item):
        """Determines whether the list contains either
        the DB column's name, attribute or field.
        """
        column_name, attribute, field = item

        if column_name in self.strings or attribute in self.strings:
            return True
        elif isinstance(field, self.fields):
            return True

        return _issubclass(field, self.field_types)


class JSONModel(Model):
    """A JSON serializable and deserializable model."""

    from_dict = classmethod(deserialize)
    patch = deserialize
    to_dict = serialize
