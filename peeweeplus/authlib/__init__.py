"""ORM models for OAuth 2.0 for authlib."""

from logging import getLogger

from peeweeplus.exceptions import MissingModule


__all__ = ['OAuth2ClientMixin']


LOGGER = getLogger(__file__)

try:
    from peeweeplus.authlib.client import OAuth2ClientMixin
except MissingModule as error:
    LOGGER.warning('Missing module "%s".', error.module)
    LOGGER.warning('OAuth2ClientMixin not available.')
else:
    __all__.append('OAuth2ClientMixin')
