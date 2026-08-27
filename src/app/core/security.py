"""OIDC client and session-based auth dependency.

Configured entirely through `settings.oauth_*`, so swapping the identity provider
(Keycloak, Okta, Auth0, PingFederate, ...) only requires updating those environment
variables, provided the new provider exposes an OIDC discovery document.
"""

from typing import Any

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request, status

from app.core.config import settings

OAUTH_CLIENT_NAME = "oauth_provider"

oauth = OAuth()
oauth.register(
    name=OAUTH_CLIENT_NAME,
    server_metadata_url=f"{settings.oauth_issuer}/.well-known/openid-configuration",
    client_id=settings.oauth_client_id,
    client_secret=settings.oauth_client_secret,
    client_kwargs={"scope": settings.oauth_scopes},
)


class NotAuthenticatedError(HTTPException):
    """Raised when a request has no authenticated session; redirects to login."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/auth/login"}
        )


def get_current_user(request: Request) -> dict[str, Any]:
    """Return the authenticated user's claims from the session, or trigger a login redirect."""
    user = request.session.get("user")
    if user is None:
        raise NotAuthenticatedError
    return dict(user)


def get_optional_user(request: Request) -> dict[str, Any] | None:
    """Return the authenticated user's claims from the session, or `None` if not logged in."""
    user = request.session.get("user")
    return dict(user) if user is not None else None
