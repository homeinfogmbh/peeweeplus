"""Sanitizing HTML."""

from lxml.html.clean import Cleaner     # pylint: disable=E0611


__all__ = ['ALLOWED_TAGS', 'sanitize']


ALLOWED_TAGS = (
    'br', 'div', 'em', 'font', 'li', 'ol', 'p', 'span', 'strong', 'table',
    'tbody', 'td', 'th', 'thead', 'tr', 'ul'
)


def sanitize(html, allow_tags=ALLOWED_TAGS):
    """Sanitizes the respective HTML text."""

    cleaner = Cleaner(allow_tags=allow_tags, remove_unknown_tags=False)
    return cleaner.clean_html(html)
