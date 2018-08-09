"""Exceptions."""

__all__ = [
    'NullError',
    'FieldValueError',
    'FieldNotNullable',
    'MissingKeyError',
    'InvalidKeys',
    'NotAField',
    'InvalidEnumerationValue',
    'PasswordTooShortError']


class NullError(TypeError):
    """Indicates that the respective field cannot be null."""

    pass


class _ModelAttrFieldKeyError(ValueError):
    """An error that stores model, attribute and fields."""

    def __init__(self, model, attr, field, key):
        """Sets the field."""
        super().__init__()
        self.model = model
        self.attr = attr
        self.field = field
        self.key = key

    def to_dict(self):
        """Returns a JSON-ish representation of this error."""
        return {
            'model': self.model.__name__,
            'attr': self.attr,
            'field': self.field.__class__.__name__,
            'key': self.key}


class FieldValueError(_ModelAttrFieldKeyError):
    """Indicates that the field cannot store data of the provided type."""

    def __init__(self, model, attr, field, key, value):
        """Sets the field and value."""
        super().__init__(model, attr, field, key)
        self.value = value

    def __str__(self):
        """Returns the respective error message."""
        return (
            'Field <{field.__class__.__name__}> from key "{key}" in column '
            '"{field.column_name}" at <{model.__name__}.{attr}> '
            'cannot store {typ}: {value}.').format(
                field=self.field, key=self.key, model=self.model,
                attr=self.attr, typ=type(self.value), value=self.value)

    def to_dict(self):
        """Returns a JSON-ish representation of this error."""
        dictionary = super().to_dict()
        dictionary.update({
            'value': str(self.value), 'type': type(self.value).__name__})
        return dictionary


class FieldNotNullable(_ModelAttrFieldKeyError):
    """Indicates that the field was assigned
    a NULL value which it cannot store.
    """

    def __str__(self):
        """Returns the respective error message."""
        return (
            'Field <{field.__class__.__name__}> from key "{key}" in column '
            '"{field.column_name}" at <{model.__name__}.{attr}> '
            'must not be NULL.').format(
                field=self.field, key=self.key, model=self.model,
                attr=self.attr)


class MissingKeyError(_ModelAttrFieldKeyError):
    """Indicates that a key was missing to deserialize the model."""

    def __str__(self):
        """Returns the respective error message."""
        return (
            'Value for field <{field.__class__.__name__}> from key "{key}" in '
            'column "{field.column_name}" at <{model.__name__}.{attr}> '
            'is missing.').format(
                field=self.field, key=self.key, model=self.model,
                attr=self.attr)


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


class NotAField(Exception):
    """Indicates that the respective attribute is not a peewee.Field."""

    def __init__(self, model, attribute):
        """Sets the model and attribute."""
        super().__init__()
        self.model = model
        self.attribute = attribute

    def __str__(self):
        """Returns the error message."""
        return 'Attribute "{}" of model "{}" is not a field.'.format(
            self.attribute, self.model)


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

    def __init__(self, pwlen, minlen):
        """Sets minimum length and actual password length."""
        super().__init__(self)
        self.pwlen = pwlen
        self.minlen = minlen

    def __str__(self):
        """Returns the respective error message."""
        return 'Password too short ({} / {} characters).'.format(
            self.pwlen, self.minlen)
