"""ORM model mixin for OAuth 2.0 clients."""

from datetime import datetime, timedelta

from peewee import Model
from peewee import BooleanField
from peewee import CharField
from peewee import DateTimeField
from peewee import IntegerField
from peewee import TextField

from peeweeplus.exceptions import MissingModule
from peeweeplus.fields import Argon2Field, JSONTextField

try:
    from authlib.common.encoding import json_loads, json_dumps
    from authlib.oauth2.rfc6749 import ClientMixin
    from authlib.oauth2.rfc6749 import TokenMixin
    from authlib.oauth2.rfc6749 import AuthorizationCodeMixin
    from authlib.oauth2.rfc6749.util import scope_to_list, list_to_scope
except ModuleNotFoundError:
    raise MissingModule('authlib')


__all__ = [
    'OAuth2ClientMixin',
    'OAuth2TokenMixin',
    'OAuth2AuthorizationCodeMixin'
]


class OAuth2ClientMixin(Model, ClientMixin):   # pylint: disable=R0904
    """An OAuth 2.0 client mixin for peewee models."""

    client_id = CharField(48, null=True, index=True)
    client_secret = Argon2Field(null=True)
    client_id_issued_at = IntegerField(default=0)
    client_secret_expires_at = IntegerField(default=0)
    client_metadata = JSONTextField(
        serialize=json_dumps, deserialize=json_loads)

    @property
    def client_info(self):
        """Implementation for Client Info in OAuth 2.0 Dynamic Client
        Registration Protocol via `Section 3.2.1`_.

        .. _`Section 3.2.1`: https://tools.ietf.org/html/rfc7591#section-3.2.1
        """
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'client_id_issued_at': self.client_id_issued_at,
            'client_secret_expires_at': self.client_secret_expires_at
        }

    @property
    def redirect_uris(self):
        """Returns a list of redirect URIs."""
        # pylint: disable=E1101
        return self.client_metadata.get('redirect_uris', [])

    @property
    def token_endpoint_auth_method(self):
        """Returns the token endpoint authentication method."""
        # pylint: disable=E1101
        return self.client_metadata.get(
            'token_endpoint_auth_method', 'client_secret_basic')

    @property
    def grant_types(self):
        """Returns a list of grant types."""
        # pylint: disable=E1101
        return self.client_metadata.get('grant_types', [])

    @property
    def response_types(self):
        """Returns a list of response types."""
        # pylint: disable=E1101
        return self.client_metadata.get('response_types', [])

    @property
    def client_name(self):
        """Returns the client's name."""
        # pylint: disable=E1101
        return self.client_metadata.get('client_name')

    @property
    def client_uri(self):
        """Returns the client's URI."""
        # pylint: disable=E1101
        return self.client_metadata.get('client_uri')

    @property
    def logo_uri(self):
        """Returns a URI to the client's logo."""
        # pylint: disable=E1101
        return self.client_metadata.get('logo_uri')

    @property
    def scope(self):
        """Returns the client's scope."""
        # pylint: disable=E1101
        return self.client_metadata.get('scope')

    @property
    def contacts(self):
        """Returns a list of contacts of the client."""
        # pylint: disable=E1101
        return self.client_metadata.get('contacts', [])

    @property
    def tos_uri(self):
        """Returns a URI to the terms of service of the client."""
        # pylint: disable=E1101
        return self.client_metadata.get('tos_uri')

    @property
    def policy_uri(self):
        """Returns a URI to the policy of the client."""
        # pylint: disable=E1101
        return self.client_metadata.get('policy_uri')

    @property
    def jwks_uri(self):
        """Returns a URI to the JSON web key set."""
        # pylint: disable=E1101
        return self.client_metadata.get('jwks_uri')

    @property
    def jwks(self):
        """Returns a list of JSON web key sets."""
        # pylint: disable=E1101
        return self.client_metadata.get('jwks', [])

    @property
    def software_id(self):
        """Returns the client's software ID."""
        # pylint: disable=E1101
        return self.client_metadata.get('software_id')

    @property
    def software_version(self):
        """Returns the client's software version."""
        # pylint: disable=E1101
        return self.client_metadata.get('software_version')

    def get_client_id(self):
        """Returns the client's ID."""
        return self.client_id

    def get_default_redirect_uri(self):
        """Returns the default redirect URI."""
        try:
            redirect_uri, *_ = self.redirect_uris
        except ValueError:
            return None

        return redirect_uri

    def get_allowed_scope(self, scope):
        """Returns the allowed scope."""
        if not scope:
            return ''

        allowed = set(self.scope.split())
        scopes = scope_to_list(scope)
        return list_to_scope([scope for scope in scopes if scope in allowed])

    def check_redirect_uri(self, redirect_uri):
        """Checks the redirect URI."""
        return redirect_uri in self.redirect_uris

    def has_client_secret(self):
        """Checks if the client's secret is set."""
        return self.client_secret is not None

    def check_client_secret(self, client_secret):
        """Verifies the client's secret."""
        # pylint: disable=E1101
        return self.client_secret.verify(client_secret)

    def check_token_endpoint_auth_method(self, method):
        """Verifies the token endpoint authentication method."""
        return self.token_endpoint_auth_method == method

    def check_response_type(self, response_type):
        """Verifies the response type."""
        return response_type in self.response_types

    def check_grant_type(self, grant_type):
        """Verifies the grant type."""
        print('DEBUG GRANT TYPE:', grant_type, self.grant_types, flush=True)
        return grant_type in self.grant_types


class OAuth2TokenMixin(Model, TokenMixin):
    """Mixin for OAuth 2.0 tokens."""

    client_id = CharField(48, null=True)
    token_type = CharField(40, null=True)
    access_token = CharField(255, unique=True)
    refresh_token = CharField(255, index=True, null=True)
    scope = TextField(default='')
    revoked = BooleanField(default=False)
    issued_at = DateTimeField(default=datetime.now)
    expires_in = IntegerField(default=0)    # Minutes.

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
        return self.issued_at + timedelta(minutes=self.expires_in)

    def is_expired(self):
        """Determines whether the token is expired."""
        return self.get_expires_at() >= datetime.now()

    def is_valid(self):
        """Determines whether the token is valid."""
        if self.revoked:
            return False

        if self.is_expired():
            return False

        return True


class OAuth2AuthorizationCodeMixin(Model, AuthorizationCodeMixin):
    """Mixin for OAuth 2.0 authorization codes."""

    code = CharField(120, unique=True)
    client_id = CharField(48, null=True)
    redirect_uri = TextField(default='')
    response_type = TextField(default='')
    scope = TextField(default='')
    nonce = TextField(null=True)
    auth_time = DateTimeField(default=datetime.now)
    code_challenge = TextField(null=True)
    code_challenge_method = CharField(48, null=True)

    def is_expired(self):
        """Determines whether the autorization code is expired."""
        return self.auth_time + timedelta(seconds=300) < datetime.now()

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
