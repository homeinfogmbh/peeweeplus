"""Exceptions."""

from typing import Iterable

from peewee import Field, ModelBase


__all__ = [
    'NullError',
    'FieldValueError',
    'FieldNotNullable',
    'MissingKeyError',
    'InvalidKeys',
    'NonUniqueValue',
    'PasswordTooShortError'
]


class NullError(TypeError):
    """Indicates that the respective field cannot be null."""


class ModelFieldError(ValueError):
    """An error that stores model, attribute and fields."""

    def __init__(self, model: ModelBase, key: str, attribute: str,
                 field: Field):
        """Sets the field."""
        super().__init__()
        self.model = model
        self.key = key
        self.attribute = attribute
        self.field = field


class FieldValueError(ModelFieldError):
    """Indicates that the field cannot store data of the provided type."""

    def __init__(self, model: ModelBase, key: str, attribute: str,
                 field: Field, value: object):
        """Sets the field and value."""
        super().__init__(model, key, attribute, field)
        self.value = value

    def __str__(self):
        """Returns the respective error message."""
        return (
            'Field <{field_type.__name__}> from key'
            ' "{key}" in column "{field.column_name}" at'
            ' <{model.__name__}.{attribute}> cannot store'
            ' {value_type.__name__}: {value}.').format(
                model=self.model, key=self.key, attribute=self.attribute,
                field=self.field, field_type=type(self.field),
                value=self.value, value_type=type(self.value))


class FieldNotNullable(ModelFieldError):
    """Indicates that the field was assigned
    a NULL value which it cannot store.
    """

    def __str__(self):
        """Returns the respective error message."""
        return (
            'Field <{field_type.__name__}> from key "{key}"'
            ' in column "{field.column_name}" at'
            ' <{model.__name__}.{attribute}> must not be NULL.').format(
                model=self.model, key=self.key, attribute=self.attribute,
                field=self.field, field_type=type(self.field))


class MissingKeyError(ModelFieldError):
    """Indicates that a key was missing to deserialize the model."""

    def __str__(self):
        """Returns the respective error message."""
        return (
            'Value for field <{field_type.__name__}> from key'
            ' "{key}" in column "{field.column_name}" at'
            ' <{model.__name__}.{attribute}> is missing.').format(
                model=self.model, key=self.key, attribute=self.attribute,
                field=self.field, field_type=type(self.field))


class InvalidKeys(ValueError):
    """Indicates that the respective keys
    can not be consumed by the model.
    """

    def __init__(self, invalid_keys: Iterable[str]):
        """Sets the respective invalid keys."""
        super().__init__(invalid_keys)
        self.invalid_keys = tuple(invalid_keys)

    def __iter__(self):
        """Yields the invalid keys."""
        yield from self.invalid_keys


class NonUniqueValue(ValueError):
    """Indicates that the respective keys can not
    be set to the respective values because the
    respective field is unique but the value is not.
    """

    def __init__(self, key: str, value: object):
        """Sets the respective invalid key→value mapping."""
        super().__init__(key, value)
        self.key = key
        self.value = value


class PasswordTooShortError(Exception):
    """Indicates that the provided password was too short."""

    def __init__(self, pwlen: int, minlen: int):
        """Sets minimum length and actual password length."""
        super().__init__(self)
        self.pwlen = pwlen
        self.minlen = minlen

    def __str__(self):
        """Returns the respective error message."""
        return f'Password too short ({self.pwlen} / {self.minlen} characters).'
