"""Mixins for OAuth 2.0 tokens."""

from time import time

from peewee import BooleanField, CharField, IntegerField, TextField

from peeweeplus.exceptions import MissingModule

try:
    from authlib.oauth2.rfc6749 import TokenMixin, AuthorizationCodeMixin
except ModuleNotFoundError:
    raise MissingModule('authlib')


__all__ = ['OAuth2TokenMixin', 'OAuth2AuthorizationCodeMixin']


class OAuth2TokenMixin(TokenMixin):
    """Mixin for OAuth 2.0 tokens."""

    client_id = CharField(48, null=True)
    token_type = CharField(40, null=True)
    access_token = CharField(255, unique=True)
    refresh_token = CharField(255, index=True, null=True)
    scope = TextField(default='')
    revoked = BooleanField(default=False)
    issued_at = IntegerField(default=lambda: int(time()))
    expires_in = IntegerField(default=0)

    def get_client_id(self):
        """Returns the client ID."""
        return self.client_id

    def get_scope(self):
        """Returns the scope."""
        return self.scope

    def get_expires_in(self):
        """Returns the amount of microseconds the token expires in."""
        return self.expires_in

    def get_expires_at(self):
        """Returns the timstamp in microseconds when the token expires."""
        return self.issued_at + self.expires_in


class OAuth2AuthorizationCodeMixin(AuthorizationCodeMixin):
    """Mixin for OAuth 2.0 authorization codes."""

    code = CharField(120, unique=True)
    client_id = CharField(48, null=True)
    redirect_uri = TextField(default='')
    response_type = TextField(default='')
    scope = TextField(default='')
    nonce = TextField(null=True)
    auth_time = IntegerField(default=lambda: int(time()))
    code_challenge = TextField(null=True)
    code_challenge_method = CharField(48, null=True)

    def is_expired(self):
        """Determines whether the autorization code is expired."""
        return self.auth_time + 300 < time()

    def get_redirect_uri(self):
        """Returns a redirect URI."""
        return self.redirect_uri

    def get_scope(self):
        """Returns the scope."""
        return self.scope

    def get_auth_time(self):
        """Returns the authentication time."""
        return self.auth_time

    def get_nonce(self):
        """Returns the nonce."""
        return self.nonce
