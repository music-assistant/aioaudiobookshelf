"""Tests for the socket client."""

import logging
from collections.abc import Callable, Coroutine
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest

from aioaudiobookshelf.client import SocketClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import (
    RefreshTokenExpiredError,
    ServiceUnavailableError,
    TokenIsMissingError,
)

Handler = Callable[..., Coroutine[Any, Any, None]]


class FakeSocketIoClient:
    """Stands in for socketio.AsyncClient and lets tests raise abs' socket events."""

    def __init__(self, **_: Any) -> None:
        """Init."""
        self.handlers: dict[str, Handler] = {}
        self.emitted: list[tuple[str, Any]] = []
        self.connected = False
        self.disconnects = 0

    def on(self, event: str, handler: Handler) -> None:
        """Register an event handler, as socketio does."""
        self.handlers[event] = handler

    async def connect(self, url: str) -> None:  # noqa: ARG002
        """Connect and raise the connect event, as socketio does."""
        self.connected = True
        await self.trigger("connect")

    async def disconnect(self) -> None:
        """Disconnect."""
        self.connected = False
        self.disconnects += 1

    async def emit(self, event: str, data: Any = None) -> None:
        """Record an emitted event."""
        self.emitted.append((event, data))

    async def trigger(self, event: str, *args: Any) -> None:
        """Raise an event abs would send."""
        await self.handlers[event](*args)

    async def auth_failed(self) -> None:
        """Raise the event abs sends for a rejected token."""
        await self.trigger("auth_failed", {"message": "Invalid token"})

    @property
    def auth_tokens(self) -> list[str]:
        """Tokens sent to abs, in order."""
        return [data for event, data in self.emitted if event == "auth"]


def _session_config(**kwargs: Any) -> SessionConfiguration:
    return SessionConfiguration(
        session=Mock(), url="http://abs.local", logger=logging.getLogger(__name__), **kwargs
    )


async def _get_socket_client(
    session_config: SessionConfiguration,
    *,
    on_refresh_token_expired: Callable[[], Any] | None = None,
) -> tuple[SocketClient, FakeSocketIoClient]:
    with patch("socketio.AsyncClient", FakeSocketIoClient):
        socket_client = SocketClient(session_config=session_config)
    socket_client.set_refresh_token_expired_callback(
        on_refresh_token_expired=on_refresh_token_expired
    )
    await socket_client.init_client()
    socket_io = socket_client.client
    assert isinstance(socket_io, FakeSocketIoClient)
    return socket_client, socket_io


async def test_expired_access_token_refreshed_on_auth_failed() -> None:
    """An access token rejected by the socket is refreshed and sent again."""
    session_config = _session_config(access_token="access1", refresh_token="refresh1")

    async def refresh() -> None:
        session_config.access_token = "access2"

    session_config.refresh = AsyncMock(side_effect=refresh)  # type: ignore[method-assign]
    _, socket_io = await _get_socket_client(session_config)

    await socket_io.auth_failed()

    assert socket_io.auth_tokens == ["access1", "access2"]


async def test_auth_retried_once_per_connection() -> None:
    """A second auth failure without a successful auth in between does not refresh again."""
    session_config = _session_config(access_token="access1", refresh_token="refresh1")
    refresh = AsyncMock()
    session_config.refresh = refresh  # type: ignore[method-assign]
    _, socket_io = await _get_socket_client(session_config)

    await socket_io.auth_failed()
    await socket_io.auth_failed()

    refresh.assert_awaited_once()


async def test_auth_retried_again_after_successful_auth() -> None:
    """A token accepted by abs restores the retry, so a later rejection refreshes again."""
    session_config = _session_config(access_token="access1", refresh_token="refresh1")
    refresh = AsyncMock()
    session_config.refresh = refresh  # type: ignore[method-assign]
    _, socket_io = await _get_socket_client(session_config)

    await socket_io.auth_failed()
    await socket_io.trigger("init", {"userId": "user1", "username": "user"})
    await socket_io.auth_failed()

    assert refresh.await_count == 2


async def test_reconnect_restores_the_retry() -> None:
    """A reconnect refreshes again, even if the previous connection gave up."""
    session_config = _session_config(access_token="access1", refresh_token="refresh1")
    refresh = AsyncMock()
    session_config.refresh = refresh  # type: ignore[method-assign]
    _, socket_io = await _get_socket_client(session_config)

    await socket_io.auth_failed()
    await socket_io.auth_failed()
    await socket_io.trigger("connect")
    await socket_io.auth_failed()

    assert refresh.await_count == 2


async def test_no_refresh_without_auto_refresh() -> None:
    """Without auto refresh the socket gives up instead of refreshing."""
    session_config = _session_config(
        access_token="access1", refresh_token="refresh1", auto_refresh=False
    )
    refresh = AsyncMock()
    session_config.refresh = refresh  # type: ignore[method-assign]
    _, socket_io = await _get_socket_client(session_config)

    await socket_io.auth_failed()

    refresh.assert_not_awaited()
    assert socket_io.auth_tokens == ["access1"]


async def test_expired_refresh_token_calls_callback() -> None:
    """An expired refresh token triggers the callback, then authenticates with its tokens."""
    session_config = _session_config(access_token="access1", refresh_token="refresh1")
    session_config.refresh = AsyncMock(side_effect=RefreshTokenExpiredError)  # type: ignore[method-assign]

    async def on_refresh_token_expired() -> None:
        session_config.access_token = "access2"

    _, socket_io = await _get_socket_client(
        session_config, on_refresh_token_expired=on_refresh_token_expired
    )

    await socket_io.auth_failed()

    assert socket_io.auth_tokens == ["access1", "access2"]


@pytest.mark.parametrize(
    "failure",
    [
        TokenIsMissingError("Refresh token not set."),
        ServiceUnavailableError,
        RefreshTokenExpiredError,
        ValueError("broken response"),
    ],
)
async def test_failing_refresh_never_escapes(failure: Exception | type[Exception]) -> None:
    """No error reaches socketio, which would drop it silently."""
    session_config = _session_config(access_token="access1", refresh_token="refresh1")
    session_config.refresh = AsyncMock(side_effect=failure)  # type: ignore[method-assign]

    async def on_refresh_token_expired() -> None:
        # the callback could not log in again, so there is no token left to send
        session_config.access_token = None

    _, socket_io = await _get_socket_client(
        session_config, on_refresh_token_expired=on_refresh_token_expired
    )

    await socket_io.auth_failed()

    assert socket_io.auth_tokens == ["access1"]


async def test_failing_callback_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    """An error raised by the callback is logged instead of vanishing."""
    session_config = _session_config(access_token="access1", refresh_token="refresh1")
    session_config.refresh = AsyncMock(side_effect=RefreshTokenExpiredError)  # type: ignore[method-assign]

    async def on_refresh_token_expired() -> None:
        raise ValueError("relogin failed")

    _, socket_io = await _get_socket_client(
        session_config, on_refresh_token_expired=on_refresh_token_expired
    )

    with caplog.at_level(logging.ERROR):
        await socket_io.auth_failed()

    assert "Could not handle a rejected socket authentication." in caplog.text


async def test_connect_error_survives_a_failing_refresh(caplog: pytest.LogCaptureFixture) -> None:
    """A connect error handler swallows nothing, so socketio keeps reconnecting."""
    session_config = _session_config(access_token="access1", refresh_token="refresh1")
    session_config.refresh = AsyncMock(side_effect=ValueError("broken response"))  # type: ignore[method-assign]
    _, socket_io = await _get_socket_client(session_config)

    with caplog.at_level(logging.ERROR):
        await socket_io.trigger("connect_error", {"message": "unauthorized"})

    assert "Could not handle a socket connection error." in caplog.text


async def test_api_key_auth_failed_disconnects() -> None:
    """A rejected api key disconnects the socket, as abs does not support it."""
    _, socket_io = await _get_socket_client(_session_config(token="api_key"))

    await socket_io.auth_failed()

    assert socket_io.disconnects == 1
    assert not socket_io.connected
