"""Tests for logout and token refresh errors."""

from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp.client_exceptions import ClientConnectionError, ClientResponseError

from aioaudiobookshelf.client import UserClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import (
    AbsError,
    ApiError,
    RefreshTokenExpiredError,
    ServiceUnavailableError,
)


def _response_error(status: int) -> ClientResponseError:
    return ClientResponseError(request_info=Mock(), history=(), status=status)


def _session_config(post: AsyncMock) -> SessionConfiguration:
    return SessionConfiguration(
        session=Mock(post=post),
        url="http://abs.local",
        access_token="access1",
        refresh_token="refresh1",
    )


def _user_client(post: AsyncMock) -> UserClient:
    client = UserClient.__new__(UserClient)
    client.session_config = _session_config(post)
    return client


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (ClientConnectionError(), ServiceUnavailableError),
        (TimeoutError(), ServiceUnavailableError),
        (_response_error(500), ApiError),
    ],
)
async def test_logout_raises_abs_error(error: Exception, expected: type[AbsError]) -> None:
    """A failing logout raises an AbsError, not a raw aiohttp error."""
    client = _user_client(AsyncMock(side_effect=error))

    with pytest.raises(expected):
        await client.logout()


async def test_logout_has_timeout() -> None:
    """Logout can't stall for aiohttp's default timeout."""
    post = AsyncMock()
    await _user_client(post).logout()

    assert post.call_args.kwargs["timeout"].total == 10


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (401, RefreshTokenExpiredError),
        (429, ServiceUnavailableError),
        (502, ServiceUnavailableError),
        (504, ServiceUnavailableError),
    ],
)
async def test_refresh_error_status(status: int, expected: type[AbsError]) -> None:
    """Only a 401 means the refresh token expired, other errors are temporary."""
    session_config = _session_config(AsyncMock(side_effect=_response_error(status)))

    with pytest.raises(expected):
        await session_config.refresh()
