"""Exceptions."""

__all__ = [
    'NullError',
    'FieldValueError',
    'FieldNotNullable',
    'MissingKeyError',
    'InvalidKeys',
    'InvalidEnumerationValue',
    'PasswordTooShortError']


class NullError(TypeError):
    """Indicates that the respective field cannot be null."""

    pass


class _ModelFieldError(ValueError):
    """An error that stores model, attribute and fields."""

    def __init__(self, model, field):
        """Sets the field."""
        super().__init__()
        self.model = model
        self.field = field


class FieldValueError(_ModelFieldError):
    """Indicates that the field cannot store data of the provided type."""

    def __init__(self, model, field, value):
        """Sets the field and value."""
        super().__init__(model, field)
        self.value = value

    def __str__(self):
        """Returns the respective error message."""
        return (
            'Field <{field.__class__.__name__}> from key'
            ' "{field.json_key}" in column "{field.column_name}" at'
            ' <{model.__name__}.{field.name}> cannot store'
            ' {value.__class__.__name__}: {value}.').format(
                model=self.model, field=self.field, value=self.value)


class FieldNotNullable(_ModelFieldError):
    """Indicates that the field was assigned
    a NULL value which it cannot store.
    """

    def __str__(self):
        """Returns the respective error message."""
        return (
            'Field <{field.__class__.__name__}> from key "{field.json_key}"'
            ' in column "{field.column_name}" at'
            ' <{model.__name__}.{field.name}> must not be NULL.').format(
            model=self.model, field=self.field)


class MissingKeyError(_ModelFieldError):
    """Indicates that a key was missing to deserialize the model."""

    def __str__(self):
        """Returns the respective error message."""
        return (
            'Value for field <{field.__class__.__name__}> from key'
            ' "{field.json_key}" in column "{field.column_name}" at'
            ' <{model.__name__}.{field.name}> is missing.').format(
                field=self.field, model=self.model)


class InvalidKeys(ValueError):
    """Indicates that the respective keys can not be consumed by the model."""

    def __init__(self, invalid_keys):
        """Sets the respective invalid keys."""
        super().__init__(invalid_keys)
        self.invalid_keys = tuple(invalid_keys)

    def __iter__(self):
        """Yields the invalid keys."""
        yield from self.invalid_keys


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
