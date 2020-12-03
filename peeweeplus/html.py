"""Sanitizing HTML."""

from functools import lru_cache
from typing import Generator

from lxml.etree import XMLSyntaxError   # pylint: disable=E0611
from lxml.html import Element, document_fromstring, tostring
from lxml.html.clean import Cleaner     # pylint: disable=E0611


__all__ = ['ALLOWED_TAGS', 'CLEANER', 'sanitize']


ALLOWED_TAGS = {
    'a', 'b', 'br', 'div', 'em', 'font', 'i', 'li', 'ol', 'p', 'span',
    'strong', 'table', 'tbody', 'td', 'th', 'thead', 'tr', 'u', 'ul'
}
CLEANER = Cleaner(allow_tags=ALLOWED_TAGS, remove_unknown_tags=False)


def get_html(element: Element) -> Generator[bytes, None, None]:
    """Returns HTML text from an element."""

    children = element.getchildren()

    # Remove <p>…</p> wrapper created by Cleaner.clean_html().
    if len(children) == 1 and children[0].tag == 'p':
        for child in children[0].iterchildren():
            yield tostring(child)
    else:
        for child in children:
            yield tostring(child)


@lru_cache(maxsize=None)
def sanitize(text: str, *, cleaner: Cleaner = CLEANER) -> str:
    """Sanitizes the respective HTML text."""

    try:
        doc = document_fromstring(text)
    except XMLSyntaxError:  # Probably not HTML text.
        return text

    return b''.join(get_html(cleaner.clean_html(doc))).decode()
