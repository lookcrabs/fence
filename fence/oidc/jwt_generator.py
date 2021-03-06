import flask
from flask_sqlalchemy_session import current_session

from fence.jwt.token import (
    generate_signed_access_token,
    generate_signed_id_token,
    generate_signed_refresh_token,
)
from fence.models import AuthorizationCode, User
from fence.oidc.errors import OIDCError
from fence.resources.google.utils import (
    get_linked_google_account_email,
    get_linked_google_account_exp,
)

from fence.settings import ACCESS_TOKEN_EXPIRES_IN, REFRESH_TOKEN_EXPIRES_IN


def generate_token(client, grant_type, **kwargs):
    """
    Generate the token response, which looks like the following:

        {
            'token_type': 'Bearer',
            'id_token': 'eyJhb[...long encoded JWT...]OnoVQ',
            'access_token': 'eyJhb[...long encoded JWT...]evfxA',
            'refresh_token': 'eyJhb[ ... long encoded JWT ... ]KnLJA',
            'expires_in': 1200,
        }

    This function will be called in authlib internals.

    Args:
        client: not used (would be used to determine expiration)
        grant_type: not used
        expires_in: not used (see expiration times configured above)
        scope (List[str]): list of requested scopes
        include_refresh_token: not used
        nonce (str): "nonsense" to include in ID token (see OIDC spec)
        refresh_token:
            for a refresh token grant, pass in the previous refresh token
            to return that same token again instead of generating a new one
            (otherwise this will let the refresh token refresh itself)
        refresh_token_claims (dict):
            also for a refresh token grant, pass the previous refresh token
            claims (to avoid having to encode or decode the refresh token
            here)
    """
    if grant_type == "authorization_code" or grant_type == "refresh_token":
        return generate_token_response(client, grant_type, **kwargs)
    elif grant_type == "implicit":
        return generate_implicit_response(client, grant_type, **kwargs)


def generate_implicit_response(
    client,
    grant_type,
    include_access_token=True,
    expires_in=None,
    user=None,
    scope=None,
    nonce=None,
    **kwargs
):
    # prevent those bothersome "not bound to session" errors
    if user not in current_session:
        user = current_session.query(User).filter_by(id=user.id).first()

    if not user:
        raise OIDCError("user not authenticated")

    keypair = flask.current_app.keypairs[0]

    linked_google_email = get_linked_google_account_email(user.id)
    linked_google_account_exp = get_linked_google_account_exp(user.id)

    if not isinstance(scope, list):
        scope = scope.split(" ")

    if not "user" in scope:
        scope.append("user")

    id_token = generate_signed_id_token(
        kid=keypair.kid,
        private_key=keypair.private_key,
        user=user,
        expires_in=ACCESS_TOKEN_EXPIRES_IN,
        client_id=client.client_id,
        audiences=scope,
        nonce=nonce,
        linked_google_email=linked_google_email,
        linked_google_account_exp=linked_google_account_exp,
    ).token

    # ``expires_in`` is just the token expiration time.
    expires_in = ACCESS_TOKEN_EXPIRES_IN

    response = {
        "token_type": "Bearer",
        "id_token": id_token,
        "expires_in": expires_in,
        # "state" handled in authlib
    }

    if include_access_token:
        access_token = generate_signed_access_token(
            kid=keypair.kid,
            private_key=keypair.private_key,
            user=user,
            expires_in=ACCESS_TOKEN_EXPIRES_IN,
            scopes=scope,
            client_id=client.client_id,
            linked_google_email=linked_google_email,
        ).token
        response["access_token"] = access_token

    return response


def generate_token_response(
    client,
    grant_type,
    expires_in=None,
    user=None,
    scope=None,
    include_refresh_token=True,
    nonce=None,
    refresh_token=None,
    refresh_token_claims=None,
    **kwargs
):
    # prevent those bothersome "not bound to session" errors
    if user not in current_session:
        user = current_session.query(User).filter_by(id=user.id).first()

    if not user:
        # Find the ``User`` model.
        # The way to do this depends on the grant type.
        if grant_type == "authorization_code":
            # For authorization code grant, get the code from either the query
            # string or the form data, and use that to look up the user.
            if flask.request.method == "GET":
                code = flask.request.args.get("code")
            else:
                code = flask.request.form.get("code")
            user = (
                current_session.query(AuthorizationCode)
                .filter_by(code=code)
                .first()
                .user
            )
        if grant_type == "refresh_token":
            # For refresh token, the user ID is the ``sub`` field in the token.
            user = (
                current_session.query(User)
                .filter_by(id=int(refresh_token_claims["sub"]))
                .first()
            )

    keypair = flask.current_app.keypairs[0]

    linked_google_email = get_linked_google_account_email(user.id)
    linked_google_account_exp = get_linked_google_account_exp(user.id)

    if not isinstance(scope, list):
        scope = scope.split(" ")

    id_token = generate_signed_id_token(
        kid=keypair.kid,
        private_key=keypair.private_key,
        user=user,
        expires_in=ACCESS_TOKEN_EXPIRES_IN,
        client_id=client.client_id,
        audiences=scope,
        nonce=nonce,
        linked_google_email=linked_google_email,
        linked_google_account_exp=linked_google_account_exp,
    ).token
    access_token = generate_signed_access_token(
        kid=keypair.kid,
        private_key=keypair.private_key,
        user=user,
        expires_in=ACCESS_TOKEN_EXPIRES_IN,
        scopes=scope,
        client_id=client.client_id,
        linked_google_email=linked_google_email,
    ).token
    # If ``refresh_token`` was passed (for instance from the refresh
    # grant), use that instead of generating a new one.
    if refresh_token is None:
        refresh_token = generate_signed_refresh_token(
            kid=keypair.kid,
            private_key=keypair.private_key,
            user=user,
            expires_in=REFRESH_TOKEN_EXPIRES_IN,
            scopes=scope,
            client_id=client.client_id,
        ).token
    # ``expires_in`` is just the access token expiration time.
    expires_in = ACCESS_TOKEN_EXPIRES_IN
    return {
        "token_type": "Bearer",
        "id_token": id_token,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": expires_in,
    }
