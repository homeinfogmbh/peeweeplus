"""HTML escaping."""

from typing import Callable

from peewee import CharField, FieldAccessor, TextField

from peeweeplus.html import sanitize


__all__ = ['HTMLCharField', 'HTMLTextField']


class HTMLTextAccessor(FieldAccessor):  # pylint: disable=R0903
    """Accessor class for HTML data."""

    def __get__(self, instance, instance_type=None):
        text = super().__get__(instance, instance_type=instance_type)

        if text is None:
            return None

        print('[DEBUG]', 'Type:', type(text), '/', 'Value:', text, flush=True)
        return self.field.clean_func(text)


class HTMLCharField(CharField):
    """CharField with HTML escaped text."""

    def __init__(self, *args, clean_func: Callable[[str], str] = sanitize,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_func = clean_func

    accessor_class = HTMLTextAccessor


class HTMLTextField(TextField):
    """TextField with HTML escaped text."""

    def __init__(self, *args, clean_func: Callable[[str], str] = sanitize,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_func = clean_func

    accessor_class = HTMLTextAccessor
