"""peewee extensions for HOMEINFO"""

from base64 import b64encode, b64decode
from contextlib import suppress
from datetime import datetime, date, time
from timelib import strpdatetime, strpdate, strptime

import peewee

__all__ = [
    'FieldValueError',
    'FieldNotNullError',
    'create',
    'dec2dom',
    'dec2dict',
    'dec2orm',
    'date2orm',
    'datetime2orm',
    'fields',
    'strffield',
    'strpfield',
    'DisabledAutoIncrement',
    'MySQLDatabase',
    'JSONModel',
    'EnumField']


TIME_FIELDS = (peewee.DateTimeField, peewee.DateField, peewee.TimeField)
BOOL_VALUES = {
    'true': True,
    'false': False,
    '1': True,
    '0': False,
    1: True,
    0: False,
    None: None}


class NullError(TypeError):
    """Indicates that the respective field
    was set to NULL but must not be NULL.
    """

    pass


class FieldValueError(ValueError):
    """Indicates that the field cannot store data of the provided type."""

    TEMPLATE = (
        '<{field.__class__.__name__} {field.db_column}> at '
        '<{model.__class__.__name__}.{attr}> cannot store {typ}: {value}.')

    def __init__(self, model, attr, field, value):
        """Sets the field and value."""
        super().__init__((model, attr, field, value))
        self.model = model
        self.attr = attr
        self.field = field
        self.value = value

    def __str__(self):
        """Returns the respective error message."""
        return self.TEMPLATE.format(
            field=self.field, model=self.model, attr=self.attr,
            typ=type(self.value), value=self.value)


class FieldNotNullError(FieldValueError):
    """Indicates that the field was assigned
    a NULL value which it cannot store.
    """

    TEMPLATE = (
        '<{field.__class__.__name__} {field.db_column}> at '
        '<{model.__class__.__name__}.{attr}> must not be NULL.')

    def __init__(self, model, attr, field):
        """Sets the field."""
        super().__init__(model, attr, field, None)

    def __str__(self):
        """Returns the respective error message."""
        return self.TEMPLATE.format(
            field=self.field, model=self.model, attr=self.attr)


def create(model):
    """Decorator for peewee.Model definitions that
    actually should be created on load.

    Usage:
        @create
        class MyModel(peewee.Model):
            pass
    """

    with suppress(peewee.OperationalError):
        with model._meta.database.execution_context():
            model.create_table(fail_silently=True)

    return model


def dec2dom(value):
    """Converts a decimal into a string."""

    if value is not None:
        return str(value)


def dec2dict(value):
    """Converts a decimal into a string."""

    if value is not None:
        return float(value)


dec2orm = dec2dict


def date2orm(value):
    """Converts a PyXB date object to a datetime.date object."""

    if value is not None:
        return value.date()


def datetime2orm(value):
    """Converts a PyXB date object to a datetime.date object."""

    if value is not None:
        return strpdatetime(value.isoformat())


def fields(model):
    """Yields fields of a peewee.Model."""

    for attr in dir(model):
        candidate = getattr(model, attr)

        if isinstance(candidate, peewee.Field):
            yield (attr, candidate)


def strffield(field, value):
    """Converts the given field's content into a string."""

    if value is not None:
        if isinstance(field, peewee.ForeignKeyField):
            return value.id
        elif isinstance(field, peewee.DecimalField):
            return float(value)
        elif isinstance(field, TIME_FIELDS):
            return value.isoformat()
        elif isinstance(field, peewee.BlobField):
            return b64encode(value)

    return value


def strpfield(value, field):
    """Converts respective value for the provided field."""

    if value is None:
        if not field.null:
            raise NullError(field)

        return value

    if isinstance(field, peewee.BooleanField):
        if isinstance(value, (bool, int)):
            return bool(value)

        try:
            return BOOL_VALUES[value]
        except KeyError:
            raise ValueError(value)
    elif isinstance(field, peewee.IntegerField):
        return int(value)
    elif isinstance(field, peewee.FloatField):
        return float(value)
    elif isinstance(field, peewee.DecimalField):
        return float(value)
    elif isinstance(field, peewee.DateTimeField):
        if isinstance(value, datetime):
            return value

        return strpdatetime(value)
    elif isinstance(field, peewee.DateField):
        if isinstance(value, date):
            return value

        return strpdate(value)
    elif isinstance(field, peewee.TimeField):
        if isinstance(value, time):
            return value

        return strptime(value)
    elif isinstance(field, peewee.BlobField):
        if isinstance(value, bytes):
            return value

        return b64decode(value)

    return value


class DisabledAutoIncrement():
    """Disables auto increment of primary key on the respective model"""

    def __init__(self, model):
        self.model = model

    def __enter__(self):
        self.model._meta.auto_increment = False
        return self

    def __exit__(self, *_):
        self.model._meta.auto_increment = True


class MySQLDatabase(peewee.MySQLDatabase):
    """Extension of peewee.MySQLDatabase with closing option"""

    def __init__(self, *args, closing=False, **kwargs):
        """Adds closing switch for automatic connection closing"""
        super().__init__(*args, **kwargs)
        self.closing = closing

    def execute_sql(self, *args, **kwargs):
        """Conditionally execute the SQL query in an
        execution context iff closing is enabled
        """
        if self.closing:
            with self.execution_context():
                return super().execute_sql(*args, **kwargs)
        else:
            return super().execute_sql(*args, **kwargs)


class JSONModel(peewee.Model):
    """A JSON-serializable model"""

    @classmethod
    def from_dict(cls, dictionary, db_column=False,
                  omit_pk=True, omit_fk=True):
        """Creates a new instance from the given dictionary."""
        record = cls()

        for attr, field in fields(cls):
            if omit_pk and isinstance(field, peewee.PrimaryKeyField):
                continue
            elif omit_fk and isinstance(field, peewee.ForeignKeyField):
                continue

            value = dictionary.get(field.db_column if db_column else attr)

            try:
                value = strpfield(value, field)
            except NullError:
                raise FieldNotNullError(cls, attr, field)
            except TypeError:
                raise FieldValueError(cls, attr, field, value)
            except ValueError:
                raise FieldValueError(cls, attr, field, value)
            else:
                setattr(record, attr, value)

        return record

    def to_dict(self, null=True, db_column=False, protected=False):
        """Returns the JSON model as a JSON-ish dictionary."""
        dictionary = {}

        for attr, field in fields(self.__class__):
            if protected or not attr.startswith('_'):
                name = field.db_column if db_column else attr
                value = getattr(self, attr)

                if value is None and not null:
                    continue

                dictionary[name] = strffield(field, value)

        return dictionary

    def patch(self, dictionary, db_column=False, omit_fk=True):
        """Patches the model with the provided dictionary values."""
        cls = self.__class__

        for attr, field in fields(cls):
            if omit_fk and isinstance(field, peewee.ForeignKeyField):
                continue

            try:
                value = dictionary[field.db_column if db_column else attr]
            except KeyError:
                continue

            try:
                value = strpfield(value, field)
            except NullError:
                raise FieldNotNullError(cls, attr, field)
            except TypeError:
                raise FieldValueError(cls, attr, field, value)
            except ValueError:
                raise FieldValueError(cls, attr, field, value)
            else:
                setattr(self, attr, value)


class EnumField(peewee.CharField):
    """CharField-based enumeration field"""

    INVALID_VALUE = 'Invalid value: "{}".'

    def __init__(self, enumeration, *args, ignore_case=False, **kwargs):
        """Initializes the enumeration field with the possible values.

        @enumeration: enum.Enum
        """
        self.enumeration = enumeration
        self.ignore_case = ignore_case
        max_length = max(len(value) for value in self.values)
        super().__init__(max_length=max_length, *args, **kwargs)

    @property
    def values(self):
        """Yieds the appropriate enumeration values."""
        for value in self.enumeration:
            yield value.value

    def is_valid(self, value):
        """Validates an enumeration value."""
        if self.ignore_case:
            return value.lower() in (value.lower() for value in self.values)

        return value in self.values

    def db_value(self, value):
        """Returns the appropriate database value."""
        if self.is_valid(value):
            return super().db_value(value)

        raise ValueError(self.INVALID_VALUE.format(value))

    def python_value(self, value):
        """Returns the appropriate python value."""
        if self.is_valid(value):
            return super().python_value(value)

        raise ValueError(self.INVALID_VALUE.format(value))
