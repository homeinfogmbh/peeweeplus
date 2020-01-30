"""ORM models for OAuth 2.0 for authlib."""

from logging import getLogger

from peeweeplus.exceptions import MissingModule


__all__ = []


LOGGER = getLogger(__file__)

try:
    from peeweeplus.authlib.client import OAuth2ClientMixin
except MissingModule as error:
    LOGGER.warning('Missing module "%s".', error.module)
    LOGGER.warning('OAuth2ClientMixin not available.')
else:
    __all__.append('OAuth2ClientMixin')

try:
    from peeweeplus.authlib.token import OAuth2TokenMixin
    from peeweeplus.authlib.token import OAuth2AuthorizationCodeMixin
except MissingModule as error:
    LOGGER.warning('Missing module "%s".', error.module)
    LOGGER.warning('OAuth2TokenMixin not available.')
    LOGGER.warning('OAuth2AuthorizationCodeMixin not available.')
else:
    __all__ += ['OAuth2TokenMixin', 'OAuth2AuthorizationCodeMixin']
