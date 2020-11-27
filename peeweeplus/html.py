"""Sanitizing HTML."""

from functools import lru_cache

from lxml.etree import XMLSyntaxError   # pylint: disable=E0611
from lxml.html import document_fromstring
from lxml.html.clean import Cleaner     # pylint: disable=E0611


__all__ = ['ALLOWED_TAGS', 'CLEANER', 'sanitize']


ALLOWED_TAGS = {
    'a', 'b', 'br', 'div', 'em', 'font', 'i', 'li', 'ol', 'p', 'span',
    'strong', 'table', 'tbody', 'td', 'th', 'thead', 'tr', 'u', 'ul'
}
CLEANER = Cleaner(allow_tags=ALLOWED_TAGS, remove_unknown_tags=False)


@lru_cache(maxsize=None)
def sanitize(text: str, *, cleaner: Cleaner = CLEANER) -> str:
    """Sanitizes the respective HTML text."""

    try:
        doc = document_fromstring(text)
    except XMLSyntaxError:  # Probably not HTML text.
        return text

    return cleaner.clean_html(doc).text_content()
