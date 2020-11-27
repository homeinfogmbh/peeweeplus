"""Sanitizing HTML."""

from functools import lru_cache
from re import compile  # pylint: disable=W0622

from lxml.etree import XMLSyntaxError   # pylint: disable=E0611
from lxml.html.clean import Cleaner     # pylint: disable=E0611


__all__ = ['ALLOWED_TAGS', 'CLEANER', 'sanitize']


ALLOWED_TAGS = {
    'a', 'br', 'div', 'em', 'font', 'i', 'li', 'ol', 'p', 'span', 'strong',
    'table', 'tbody', 'td', 'th', 'thead', 'tr', 'u', 'ul'
}
CLEANER = Cleaner(allow_tags=ALLOWED_TAGS, remove_unknown_tags=False)
P_TAG = '<p>'
P_REGEX = compile('<p>(.*)</p>')


@lru_cache(maxsize=None)
def sanitize(text: str, *, cleaner: Cleaner = CLEANER) -> str:
    """Sanitizes the respective HTML text."""

    try:
        cleaned_text = cleaner.clean_html(text)
    except XMLSyntaxError:  # Probably not HTML text.
        return text

    if not text.startswith(P_TAG):
        match = P_REGEX.fullmatch(cleaned_text)

        if match is not None:
            return match.group(1)

    return cleaned_text
