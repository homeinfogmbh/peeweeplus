"""Exceptions."""

__all__ = [
    'FieldValueError',
    'FieldNotNullable',
    'MissingKeyError',
    'InvalidKeys',
    'InvalidEnumerationValue',
    'PasswordTooShortError']


class _ModelAttrFieldError(ValueError):
    """An error that stores model, attribute and fields."""

    def __init__(self, model, attr, field):
        """Sets the field."""
        super().__init__()
        self.model = model
        self.attr = attr
        self.field = field

    def to_dict(self):
        """Returns a JSON-ish representation of this error."""
        return {
            'model': self.model.__name__,
            'field': self.field.__class__.__name__,
            'key': self.field.column_name}


class FieldValueError(_ModelAttrFieldError):
    """Indicates that the field cannot store data of the provided type."""

    def __init__(self, model, attr, field, value):
        """Sets the field and value."""
        super().__init__(model, attr, field)
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
        dictionary = super().to_dict()
        dictionary.update({
            'value': str(self.value),
            'type': type(self.value).__name__})
        return dictionary


class FieldNotNullable(_ModelAttrFieldError):
    """Indicates that the field was assigned
    a NULL value which it cannot store.
    """

    def __str__(self):
        """Returns the respective error message."""
        return (
            '<{field.__class__.__name__} {field.column_name}> at '
            '<{model.__class__.__name__}.{attr}> must not be NULL.').format(
                field=self.field, model=self.model, attr=self.attr)


class MissingKeyError(_ModelAttrFieldError):
    """Indicates that a key was missing to deserialize the model."""

    def __str__(self):
        """Returns the respective error message."""
        return (
            'Valaue for <{field.__class__.__name__} {field.column_name}> at '
            '<{model.__class__.__name__}.{attr}> is missing.').format(
                field=self.field, model=self.model, attr=self.attr)


class InvalidKeys(ValueError):
    """Indicates that the respective keys can not be consumed by the model."""

    def __init__(self, invalid_keys):
        """Sets the respective invalid keys."""
        super().__init__(invalid_keys)
        self.invalid_keys = tuple(invalid_keys)

    def __iter__(self):
        """Yields the invalid keys."""
        yield from self.invalid_keys

    def to_dict(self):
        """Returns a JSON-ish dictionary."""
        return {'keys': self.invalid_keys}


class InvalidEnumerationValue(ValueError):
    """Indicates that an invalid enumeration value has been specified."""

    def __init__(self, value, enum):
        """Sets the respective enumeration and invalid value."""
        super().__init__('Invalid enum value: "{}".'.format(value))
        self.value = value
        self.enum = enum

    def to_dict(self):
        """Returns a JSON-ish dictionary."""
        return {
            'invalid': self.value,
            'allowed': [value.value for value in self.enum]}


class PasswordTooShortError(Exception):
    """Indicates that the provided password was too short."""

    def __init__(self, minlen, pwlen):
        """Sets minimum length and actual password length."""
        super().__init__(self, minlen, pwlen)
        self.minlen = minlen
        self.pwlen = pwlen

    def __str__(self):
        """Returns the respective error message."""
        return 'Password too short ({} / {} characters).'.format(
            self.pwlen, self.minlen)
