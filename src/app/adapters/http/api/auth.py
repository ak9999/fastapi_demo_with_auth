"""Authentication routes implementing the OIDC authorization code flow."""

from typing import Any

import httpx
from authlib.integrations.base_client.errors import OAuthError
from fastapi import APIRouter, HTTPException, Request, status
from starlette.responses import RedirectResponse

from app.core.security import OAUTH_CLIENT_NAME, oauth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(request: Request) -> RedirectResponse:
    """Redirect the user to the OIDC provider to begin the authorization code flow."""
    client = oauth.create_client(OAUTH_CLIENT_NAME)
    redirect_uri = request.url_for("callback")
    try:
        response: RedirectResponse = await client.authorize_redirect(
            request, redirect_uri
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to reach the identity provider. Please try again later.",
        ) from exc
    return response


@router.get("/callback")
async def callback(request: Request) -> RedirectResponse:
    """Handle the redirect back from the OIDC provider, exchange the code, and store the user session."""
    client = oauth.create_client(OAUTH_CLIENT_NAME)
    try:
        token: dict[str, Any] = await client.authorize_access_token(request)
        user_info = token.get("userinfo")
        if user_info is None:
            user_info = await client.userinfo(token=token)
    except OAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {exc.description or exc.error}",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to reach the identity provider. Please try again later.",
        ) from exc
    request.session["user"] = dict(user_info)
    return RedirectResponse(url="/")


@router.get("/logout")
def logout(request: Request) -> RedirectResponse:
    """Clear the local session, logging the user out of the application."""
    request.session.pop("user", None)
    return RedirectResponse(url="/")
