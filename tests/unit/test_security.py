"""Unit tests for auth session helpers."""

from unittest.mock import MagicMock

import pytest

from app.core.security import NotAuthenticatedError, get_current_user, get_optional_user


def _request_with_session(session: dict[str, object]) -> MagicMock:
    request = MagicMock()
    request.session = session
    return request


def test_get_current_user_returns_user_when_present() -> None:
    request = _request_with_session({"user": {"sub": "abc"}})

    assert get_current_user(request) == {"sub": "abc"}


def test_get_current_user_raises_when_missing() -> None:
    request = _request_with_session({})

    with pytest.raises(NotAuthenticatedError):
        get_current_user(request)


def test_get_optional_user_returns_none_when_missing() -> None:
    request = _request_with_session({})

    assert get_optional_user(request) is None


def test_get_optional_user_returns_user_when_present() -> None:
    request = _request_with_session({"user": {"sub": "abc"}})

    assert get_optional_user(request) == {"sub": "abc"}
