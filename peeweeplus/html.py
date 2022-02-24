"""Sanitizing HTML."""

from functools import lru_cache
from html import unescape
from typing import Iterator

from lxml.etree import ParserError, XMLSyntaxError
from lxml.html import Element, document_fromstring, tostring
from lxml.html.clean import Cleaner


__all__ = ['ALLOWED_TAGS', 'CLEANER', 'sanitize']


ALLOWED_TAGS = {
    'a', 'b', 'br', 'div', 'em', 'font', 'i', 'li', 'ol', 'p', 'span',
}
CLEANER = Cleaner(allow_tags=ALLOWED_TAGS, remove_unknown_tags=False)


def get_html_strings(element: Element) -> Iterator[str]:
    """Yields HTML-text from an element."""

    try:
        first, *children = element.getchildren()
    except ValueError:
        yield tostring(element).decode()
        return

    # Remove <p>…</p> wrapper created by Cleaner.clean_html().
    if not children and first.tag == 'p':
        if first.text:
            yield first.text

        for child in first.iterchildren():
            yield tostring(child).decode()
    else:
        for child in element.iterchildren():
            yield tostring(child).decode()


@lru_cache(maxsize=None)
def sanitize(text: str, *, cleaner: Cleaner = CLEANER) -> str:
    """Sanitizes the respective HTML text."""

    try:
        doc = document_fromstring(text)
    except (ParserError, XMLSyntaxError):  # Probably not HTML text.
        return text

    return ''.join(map(unescape, get_html_strings(cleaner.clean_html(doc))))
