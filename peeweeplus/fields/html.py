"""HTML escaping."""

from lxml.html.clean import Cleaner     # pylint: disable=E0611

from peewee import CharField, FieldAccessor, TextField

from peeweeplus.html import CLEANER


__all__ = ['HTMLCharField', 'HTMLTextField']


class HTMLTextAccessor(FieldAccessor):  # pylint: disable=R0903
    """Accessor class for HTML data."""

    def __get__(self, instance, instance_type=None):
        text = super().__get__(instance, instance_type=instance_type)

        if text is None:
            return None

        return self.field.cleaner.clean_html(text)


class HTMLCharField(CharField):
    """CharField with HTML escaped text."""

    def __init__(self, *args, cleaner: Cleaner = CLEANER, **kwargs):
        super().__init__(*args, **kwargs)
        self.cleaner = cleaner

    accessor_class = HTMLTextAccessor


class HTMLTextField(TextField):
    """TextField with HTML escaped text."""

    def __init__(self, *args, cleaner: Cleaner = CLEANER, **kwargs):
        super().__init__(*args, **kwargs)
        self.cleaner = cleaner

    accessor_class = HTMLTextAccessor
