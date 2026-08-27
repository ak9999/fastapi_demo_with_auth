"""Integration tests for OIDC-guarded routes."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from authlib.integrations.base_client.errors import OAuthError
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse

from app.core.security import get_optional_user
from app.main import app


def test_read_root_shows_login_link_when_unauthenticated() -> None:
    client = TestClient(app, follow_redirects=False)

    response = client.get("/")

    assert response.status_code == 200
    assert 'href="/auth/login"' in response.text
    assert "Please log in" in response.text


@pytest.fixture
def authenticated_client() -> Generator[TestClient]:
    app.dependency_overrides[get_optional_user] = lambda: {
        "sub": "user-123",
        "name": "Jane Doe",
    }
    try:
        yield TestClient(app, follow_redirects=False)
    finally:
        del app.dependency_overrides[get_optional_user]


def test_read_root_returns_greeting_when_authenticated(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.get("/")

    assert response.status_code == 200
    assert "Hello, Jane Doe!" in response.text
    assert 'href="/auth/logout"' in response.text


def test_read_root_escapes_user_supplied_name() -> None:
    app.dependency_overrides[get_optional_user] = lambda: {
        "sub": "user-123",
        "name": "<script>",
    }
    try:
        client = TestClient(app, follow_redirects=False)
        response = client.get("/")
    finally:
        del app.dependency_overrides[get_optional_user]

    assert "<script>" not in response.text
    assert "&lt;script&gt;" in response.text


def test_callback_returns_401_when_oauth_exchange_fails() -> None:
    client = TestClient(app, follow_redirects=False)
    fake_client = AsyncMock()
    fake_client.authorize_access_token.side_effect = OAuthError(
        error="invalid_grant", description="Authorization code expired"
    )

    with patch(
        "app.adapters.http.api.auth.oauth.create_client", return_value=fake_client
    ):
        response = client.get("/auth/callback")

    assert response.status_code == 401
    assert response.json() == {"detail": "Login failed: Authorization code expired"}


def test_login_redirects_to_identity_provider() -> None:
    client = TestClient(app, follow_redirects=False)
    fake_client = AsyncMock()
    fake_client.authorize_redirect.return_value = RedirectResponse(
        url="https://idp.example/auth"
    )

    with patch(
        "app.adapters.http.api.auth.oauth.create_client", return_value=fake_client
    ):
        response = client.get("/auth/login")

    assert response.status_code == 307
    assert response.headers["location"] == "https://idp.example/auth"


def test_login_returns_502_when_identity_provider_unreachable() -> None:
    client = TestClient(app, follow_redirects=False)
    fake_client = AsyncMock()
    fake_client.authorize_redirect.side_effect = httpx.ConnectError("boom")

    with patch(
        "app.adapters.http.api.auth.oauth.create_client", return_value=fake_client
    ):
        response = client.get("/auth/login")

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Unable to reach the identity provider. Please try again later."
    }


def test_callback_returns_502_when_identity_provider_unreachable() -> None:
    client = TestClient(app, follow_redirects=False)
    fake_client = AsyncMock()
    fake_client.authorize_access_token.side_effect = httpx.ConnectError("boom")

    with patch(
        "app.adapters.http.api.auth.oauth.create_client", return_value=fake_client
    ):
        response = client.get("/auth/callback")

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Unable to reach the identity provider. Please try again later."
    }


def test_callback_uses_userinfo_from_token_when_present() -> None:
    client = TestClient(app, follow_redirects=False)
    fake_client = AsyncMock()
    fake_client.authorize_access_token.return_value = {
        "userinfo": {"sub": "user-123", "name": "Jane Doe"}
    }

    with patch(
        "app.adapters.http.api.auth.oauth.create_client", return_value=fake_client
    ):
        response = client.get("/auth/callback")

    assert response.status_code == 307
    assert response.headers["location"] == "/"
    fake_client.userinfo.assert_not_called()


def test_callback_fetches_userinfo_when_absent_from_token() -> None:
    client = TestClient(app, follow_redirects=False)
    fake_client = AsyncMock()
    fake_client.authorize_access_token.return_value = {"access_token": "abc"}
    fake_client.userinfo.return_value = {"sub": "user-123", "name": "Jane Doe"}

    with patch(
        "app.adapters.http.api.auth.oauth.create_client", return_value=fake_client
    ):
        response = client.get("/auth/callback")

    assert response.status_code == 307
    fake_client.userinfo.assert_awaited_once()


def test_logout_clears_session() -> None:
    client = TestClient(app, follow_redirects=False)

    response = client.get("/auth/logout")

    assert response.status_code == 307
    assert response.headers["location"] == "/"
