"""ORM model mixin for OAuth 2.0 clients."""

from datetime import datetime, timedelta
from typing import Iterator

from argon2.exceptions import VerifyMismatchError
from authlib.common.encoding import json_loads, json_dumps
from authlib.oauth2.rfc6749 import ClientMixin
from authlib.oauth2.rfc6749 import TokenMixin
from authlib.oauth2.rfc6749 import AuthorizationCodeMixin
from authlib.oauth2.rfc6749.util import scope_to_list, list_to_scope

from peewee import Model
from peewee import ModelBase
from peewee import BooleanField
from peewee import CharField
from peewee import DateTimeField
from peewee import ForeignKeyField
from peewee import IntegerField
from peewee import TextField

from peeweeplus.fields import Argon2Field, JSONTextField


__all__ = [
    'OAuth2ClientMixin',
    'OAuth2TokenMixin',
    'OAuth2AuthorizationCodeMixin',
    'RedirectURIMixin',
    'GrantTypeMixin',
    'ResponseTypeMixin',
    'ScopeMixin',
    'ContactMixin',
    'JWKSMixin'
]


class OAuth2ClientMixin(Model, ClientMixin):   # pylint: disable=R0904
    """An OAuth 2.0 client mixin for peewee models."""

    client_id = CharField(48, null=True, index=True)
    client_secret = Argon2Field(null=True)
    client_id_issued_at = IntegerField(default=0)
    client_secret_expires_at = IntegerField(default=0)
    # Meta data.
    token_endpoint_auth_method = TextField(null=True)
    client_name = TextField(null=True)
    client_uri = TextField(null=True)
    logo_uri = TextField(null=True)
    tos_uri = TextField(null=True)
    policy_uri = TextField(null=True)
    jwks_uri = TextField(null=True)
    software_id = TextField(null=True)
    software_version = TextField(null=True)

    @classmethod
    def get_related_models(cls, model: ModelBase = Model) -> Iterator[Model]:
        """Yields related models."""
        for mixin, backref in CLIENT_RELATED_MIXINS:
            yield cls._get_related_model(model, mixin, backref)

    @classmethod
    def _get_related_model(cls, model: ModelBase, mixin: type,
                           backref: str) -> Model:
        """Returns an implementation of the related model."""
        class ClientRelatedModel(model, mixin):  # pylint: disable=C0115,R0903
            class Meta:     # pylint: disable=C0115,R0903
                table_name = backref

            client = ForeignKeyField(
                cls, column_name='client', backref=backref,
                on_delete='CASCADE', on_update='CASCADE')

        ClientRelatedModel.__doc__ = f'Implementation of {mixin.__name__}.'
        return ClientRelatedModel

    @property
    def client_info(self) -> dict:
        """Implementation for Client Info in OAuth 2.0 Dynamic Client
        Registration Protocol via `Section 3.2.1`.

        `Section 3.2.1`: https://tools.ietf.org/html/rfc7591#section-3.2.1
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
        raise NotImplementedError()

    @property
    def grant_types(self):
        """Returns a list of grant types."""
        raise NotImplementedError()

    @property
    def response_types(self):
        """Returns a list of response types."""
        raise NotImplementedError()

    @property
    def scopes(self):
        """Returns a list of allowed scopes."""
        raise NotImplementedError()

    @property
    def contacts(self):
        """Returns a list of contacts of the client."""
        raise NotImplementedError()

    @property
    def jwks(self):
        """Returns a list of JSON web key sets."""
        raise NotImplementedError()

    def get_client_id(self):
        """Returns the client's ID."""
        return self.client_id

    def get_default_redirect_uri(self) -> str:
        """Returns the default redirect URI."""
        try:
            redirect_uri, *_ = self.redirect_uris
        except ValueError:
            return None

        return redirect_uri

    def get_allowed_scope(self, scope: str) -> str:
        """Returns the allowed scope."""
        if not scope:
            return ''

        allowed = {scope.scope for scope in self.scopes}
        scopes = scope_to_list(scope)
        return list_to_scope([scope for scope in scopes if scope in allowed])

    def check_redirect_uri(self, redirect_uri: str) -> bool:
        """Checks the redirect URI."""
        return redirect_uri in {uri.uri for uri in self.redirect_uris}

    def has_client_secret(self) -> bool:
        """Checks if the client's secret is set."""
        return self.client_secret is not None

    def check_client_secret(self, client_secret: str) -> bool:
        """Verifies the client's secret."""
        # pylint: disable=E1101
        try:
            return self.client_secret.verify(client_secret)
        except VerifyMismatchError:
            return False

    def check_endpoint_auth_method(self, method: str, endpoint: str) -> bool:
        """Checks the authorization for the respective endpoint."""
        print('Endpoint auth check:', method, '@', endpoint, flush=True)

        if endpoint == 'token':
            return self.token_endpoint_auth_method == method

        return False

    def check_response_type(self, response_type: str) -> bool:
        """Verifies the response type."""
        return response_type in {typ.type for typ in self.response_types}

    def check_grant_type(self, grant_type: str) -> bool:
        """Verifies the grant type."""
        return grant_type in {typ.type for typ in self.grant_types}


class OAuth2TokenMixin(Model, TokenMixin):
    """Mixin for OAuth 2.0 tokens."""

    client_id = CharField(48, null=True)
    token_type = CharField(40, null=True)
    access_token = CharField(255, unique=True)
    refresh_token = CharField(255, index=True, null=True)
    scope = TextField(default='')
    revoked = BooleanField(default=False)
    issued_at = DateTimeField(default=datetime.now)
    expires_in = IntegerField(default=0)    # Seconds.

    @property
    def expires_at(self) -> datetime:
        """Returns the datetime when the token expires."""
        return self.issued_at + timedelta(seconds=self.expires_in)

    def get_client_id(self) -> str:
        """Returns the client ID."""
        return self.client_id

    def get_scope(self) -> str:
        """Returns the scope."""
        return self.scope

    def get_expires_in(self) -> int:
        """Returns the amount of microseconds the token expires in."""
        return self.expires_in

    def get_expires_at(self) -> int:
        """Returns the timstamp in microseconds when the token expires."""
        return self.expires_at.timestamp()

    def is_expired(self) -> bool:
        """Determines whether the token is expired."""
        return self.expires_at <= datetime.now()

    def is_valid(self) -> bool:
        """Determines whether the token is valid."""
        return not self.revoked and not self.is_expired()


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

    def is_expired(self) -> bool:
        """Determines whether the autorization code is expired."""
        return self.auth_time + timedelta(seconds=300) < datetime.now()

    def get_redirect_uri(self) -> str:
        """Returns a redirect URI."""
        return self.redirect_uri

    def get_scope(self) -> str:
        """Returns the scope."""
        return self.scope

    def get_auth_time(self) -> datetime:
        """Returns the authentication time."""
        return self.auth_time

    def get_nonce(self) -> str:
        """Returns the nonce."""
        return self.nonce


class RedirectURIMixin(Model):  # pylint: disable=R0903
    """A redirect URI mixin."""

    uri = TextField()


class GrantTypeMixin(Model):    # pylint: disable=R0903
    """A grant type mixin."""

    type = TextField()


class ResponseTypeMixin(Model):     # pylint: disable=R0903
    """A response type mixin."""

    type = TextField()


class ScopeMixin(Model):    # pylint: disable=R0903
    """A scope mixin."""

    scope = TextField()


class ContactMixin(Model):  # pylint: disable=R0903
    """A contact mixin."""

    contact = TextField()


class JWKSMixin(Model):     # pylint: disable=R0903
    """A JSON web key set mixin."""

    jwk = JSONTextField(serialize=json_dumps, deserialize=json_loads)


CLIENT_RELATED_MIXINS = (
    (RedirectURIMixin, 'redirect_uris'),
    (GrantTypeMixin, 'grant_types'),
    (ResponseTypeMixin, 'response_types'),
    (ScopeMixin, 'scopes'),
    (ContactMixin, 'contacts'),
    (JWKSMixin, 'jwks')
)
