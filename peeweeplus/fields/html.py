"""HTML escaping."""

from typing import Callable, Optional

from peewee import CharField, FieldAccessor, TextField

from peeweeplus.html import sanitize


__all__ = ["HTMLCharField", "HTMLTextField"]


class HTMLTextAccessor(FieldAccessor):
    """Accessor class for HTML data."""

    def __get__(self, instance: type, instance_type: Optional[type] = None):
        value = super().__get__(instance, instance_type=instance_type)

        if instance is None:
            return value

        if value is None:
            return None

        return self.field.clean_func(value)


class HTMLCharField(CharField):
    """CharField with HTML escaped text."""

    accessor_class = HTMLTextAccessor

    def __init__(self, *args, clean_func: Callable[[str], str] = sanitize, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_func = clean_func


class HTMLTextField(TextField):
    """TextField with HTML escaped text."""

    accessor_class = HTMLTextAccessor

    def __init__(self, *args, clean_func: Callable[[str], str] = sanitize, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_func = clean_func
