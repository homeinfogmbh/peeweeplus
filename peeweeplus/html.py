"""Sanitizing HTML."""

from functools import lru_cache

from lxml.etree import XMLSyntaxError   # pylint: disable=E0611
from lxml.html.clean import Cleaner     # pylint: disable=E0611


__all__ = ['ALLOWED_TAGS', 'CLEANER', 'sanitize']


ALLOWED_TAGS = {
    'br', 'div', 'em', 'font', 'li', 'ol', 'p', 'span', 'strong', 'table',
    'tbody', 'td', 'th', 'thead', 'tr', 'ul'
}
CLEANER = Cleaner(
    allow_tags=ALLOWED_TAGS,
    remove_unknown_tags=False,
    page_structure=True
)


@lru_cache()
def sanitize(text: str, *, cleaner: Cleaner = CLEANER) -> str:
    """Sanitizes the respective HTML text."""

    try:
        return cleaner.clean_html(text)
    except XMLSyntaxError:  # Probably not HTML text.
        return text
