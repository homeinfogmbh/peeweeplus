"""Exceptions."""

__all__ = [
    'NullError',
    'FieldValueError',
    'FieldNotNullable',
    'MissingKeyError',
    'InvalidKeys',
    'NonUniqueValue',
    'InvalidEnumerationValue',
    'PasswordTooShortError']


class NullError(TypeError):
    """Indicates that the respective field cannot be null."""

    pass


class _ModelFieldError(ValueError):
    """An error that stores model, attribute and fields."""

    def __init__(self, model, key, attribute, field):
        """Sets the field."""
        super().__init__()
        self.model = model
        self.key = key
        self.attribute = attribute
        self.field = field


class FieldValueError(_ModelFieldError):
    """Indicates that the field cannot store data of the provided type."""

    def __init__(self, model, key, attribute, field, value):
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


class FieldNotNullable(_ModelFieldError):
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


class MissingKeyError(_ModelFieldError):
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

    def __init__(self, invalid_keys):
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

    def __init__(self, key, value):
        """Sets the respective invalid key→value mapping."""
        super().__init__(key, value)
        self.key = key
        self.value = value


class InvalidEnumerationValue(ValueError):
    """Indicates that an invalid enumeration value has been specified."""

    def __init__(self, value, enum):
        """Sets the respective enumeration and invalid value."""
        super().__init__('Invalid enum value: "{}".'.format(value))
        self.value = value
        self.enum = enum


class PasswordTooShortError(Exception):
    """Indicates that the provided password was too short."""

    def __init__(self, pwlen, minlen):
        """Sets minimum length and actual password length."""
        super().__init__(self)
        self.pwlen = pwlen
        self.minlen = minlen

    def __str__(self):
        """Returns the respective error message."""
        return 'Password too short ({} / {} characters).'.format(
            self.pwlen, self.minlen)
