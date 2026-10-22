"""Tests for the socket client."""

import logging
from collections.abc import Callable, Coroutine
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
import socketio.exceptions

from aioaudiobookshelf.client import SocketClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import (
    RefreshTokenExpiredError,
    ServiceUnavailableError,
    TokenIsMissingError,
)

Handler = Callable[..., Coroutine[Any, Any, None]]

# what the handlers log for an error they did not expect
GUARD_LOG = "Could not handle a rejected socket authentication."
CALLBACK_LOG = "The refresh token expired callback failed."


class FakeSocketIoClient:
    """Stands in for socketio.AsyncClient and lets tests raise abs' socket events."""

    def __init__(self, **_: Any) -> None:
        """Init."""
        self.handlers: dict[str, Handler] = {}
        self.emitted: list[tuple[str, Any]] = []
        self.url: str | None = None
        self.socketio_path: str | None = None
        self.options: dict[str, Any] = {}
        self.disconnects = 0

    def on(self, event: str, handler: Handler) -> None:
        """Register an event handler."""
        self.handlers[event] = handler

    async def connect(self, url: str, socketio_path: str, **options: Any) -> None:
        """Connect and raise the connect event, as socketio does."""
        self.url = url
        self.socketio_path = socketio_path
        self.options = options
        await self.trigger("connect")

    async def disconnect(self) -> None:
        """Disconnect."""
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


def _session_config(refresh: Any = None, **kwargs: Any) -> SessionConfiguration:
    kwargs.setdefault("url", "http://abs.local")
    session_config = SessionConfiguration(
        session=Mock(), logger=logging.getLogger(__name__), **kwargs
    )
    if refresh is not None:
        session_config.refresh = refresh  # type: ignore[method-assign]
    return session_config


async def _socket(
    session_config: SessionConfiguration,
    *,
    on_refresh_token_expired: Callable[[], Any] | None = None,
    **user_callbacks: Any,
) -> FakeSocketIoClient:
    """Connect a socket client which talks to the fake instead of socketio."""
    with patch("socketio.AsyncClient", FakeSocketIoClient):
        socket_client = SocketClient(session_config=session_config)
    socket_client.set_refresh_token_expired_callback(
        on_refresh_token_expired=on_refresh_token_expired
    )
    if user_callbacks:
        socket_client.set_user_callbacks(**user_callbacks)
    await socket_client.init_client()
    assert isinstance(socket_client.client, FakeSocketIoClient)
    return socket_client.client


async def test_expired_access_token_refreshed_on_auth_failed() -> None:
    """An access token rejected by the socket is refreshed and sent again."""
    session_config = _session_config(access_token="access1", refresh_token="refresh1")

    async def refresh() -> None:
        session_config.access_token = "access2"

    session_config.refresh = AsyncMock(side_effect=refresh)  # type: ignore[method-assign]
    socket_io = await _socket(session_config)

    await socket_io.auth_failed()

    assert socket_io.auth_tokens == ["access1", "access2"]


async def test_auth_retried_only_once() -> None:
    """A second rejection without an accepted token in between does not refresh again."""
    refresh = AsyncMock()
    socket_io = await _socket(
        _session_config(refresh, access_token="access1", refresh_token="refresh1")
    )

    await socket_io.auth_failed()
    await socket_io.auth_failed()

    refresh.assert_awaited_once()


@pytest.mark.parametrize("accepted", [("init", {"userId": "user1"}), ("connect",)])
async def test_retry_restored_by_a_working_socket(accepted: tuple[Any, ...]) -> None:
    """Abs accepting a token, and a reconnect, both restore the single retry."""
    refresh = AsyncMock()
    socket_io = await _socket(
        _session_config(refresh, access_token="access1", refresh_token="refresh1")
    )

    await socket_io.auth_failed()
    await socket_io.trigger(*accepted)
    await socket_io.auth_failed()

    assert refresh.await_count == 2


async def test_no_refresh_without_auto_refresh() -> None:
    """Without auto refresh the socket gives up instead of refreshing."""
    refresh = AsyncMock()
    socket_io = await _socket(
        _session_config(
            refresh, access_token="access1", refresh_token="refresh1", auto_refresh=False
        )
    )

    await socket_io.auth_failed()

    refresh.assert_not_awaited()
    assert socket_io.auth_tokens == ["access1"]


async def test_expired_refresh_token_calls_callback() -> None:
    """An expired refresh token triggers the callback, then authenticates with its tokens."""
    session_config = _session_config(
        AsyncMock(side_effect=RefreshTokenExpiredError),
        access_token="access1",
        refresh_token="refresh1",
    )

    async def on_refresh_token_expired() -> None:
        session_config.access_token = "access2"

    socket_io = await _socket(session_config, on_refresh_token_expired=on_refresh_token_expired)

    await socket_io.auth_failed()

    assert socket_io.auth_tokens == ["access1", "access2"]


@pytest.mark.parametrize("failure", [ServiceUnavailableError, TokenIsMissingError])
async def test_known_refresh_failure_handled_quietly(
    failure: type[Exception], caplog: pytest.LogCaptureFixture
) -> None:
    """A refresh error the socket expects leaves it to reconnect, without logging a fault."""
    socket_io = await _socket(
        _session_config(
            AsyncMock(side_effect=failure), access_token="access1", refresh_token="refresh1"
        )
    )

    with caplog.at_level(logging.ERROR):
        await socket_io.auth_failed()

    assert socket_io.auth_tokens == ["access1"]
    assert GUARD_LOG not in caplog.text


async def test_a_failing_callback_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    """The callback belongs to the caller, and socketio would drop what it raises."""

    async def on_refresh_token_expired() -> None:
        raise ValueError("relogin failed")

    socket_io = await _socket(
        _session_config(
            AsyncMock(side_effect=RefreshTokenExpiredError),
            access_token="access1",
            refresh_token="refresh1",
        ),
        on_refresh_token_expired=on_refresh_token_expired,
    )

    with caplog.at_level(logging.ERROR):
        await socket_io.auth_failed()

    assert CALLBACK_LOG in caplog.text


async def test_a_socketio_error_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    """Socketio runs the handler in its own task and drops whatever it raises."""
    socket_io = await _socket(_session_config(token="api_key"))
    socket_io.disconnect = AsyncMock(  # type: ignore[method-assign]
        side_effect=socketio.exceptions.BadNamespaceError
    )

    with caplog.at_level(logging.ERROR):
        await socket_io.auth_failed()

    assert GUARD_LOG in caplog.text


async def test_connect_error_does_not_spend_a_refresh() -> None:
    """A socket which cannot reach abs has not had its token rejected."""
    refresh = AsyncMock()
    socket_io = await _socket(
        _session_config(refresh, access_token="access1", refresh_token="refresh1")
    )

    await socket_io.trigger("connect_error", {"message": "unauthorized"})

    refresh.assert_not_awaited()


async def test_api_key_auth_failed_disconnects(caplog: pytest.LogCaptureFixture) -> None:
    """An api key abs rejected cannot be refreshed, so the socket goes down and says why."""
    socket_io = await _socket(_session_config(token="api_key"))

    with caplog.at_level(logging.WARNING):
        await socket_io.trigger("auth_failed", {"message": "API key expired"})

    assert socket_io.disconnects == 1
    assert "Abs said: API key expired." in caplog.text


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("http://abs.local", "/socket.io"),
        ("http://abs.local:13378", "/socket.io"),
        ("https://example.com/abs", "/abs/socket.io"),
        ("https://example.com/audiobooks/", "/audiobooks/socket.io"),
    ],
)
async def test_socket_path_follows_the_url(url: str, expected: str) -> None:
    """A base path in the configured url has to reach the socket as well."""
    socket_io = await _socket(_session_config(url=url, access_token="access1"))

    assert socket_io.socketio_path == expected


async def test_user_session_closed_reaches_the_callback() -> None:
    """Abs sends the id of the session it closed, see its PlaybackSessionManager.js."""
    closed: list[str] = []

    async def on_user_session_closed(session_id: str) -> None:
        closed.append(session_id)

    socket_io = await _socket(
        _session_config(access_token="access1"),
        on_user_session_closed=on_user_session_closed,
    )

    await socket_io.trigger("user_session_closed", "session1")

    assert closed == ["session1"]


async def test_a_connect_without_a_token_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    """Socketio drops what a handler raises, so the connect handler has to log it itself."""
    with caplog.at_level(logging.ERROR):
        await _socket(_session_config())

    assert "Could not authenticate the socket connection." in caplog.text


async def test_an_unreadable_event_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    """A schema gap in a live event must not stop the updates silently."""
    socket_io = await _socket(_session_config(access_token="access1"), on_user_updated=AsyncMock())

    with caplog.at_level(logging.ERROR):
        await socket_io.trigger("user_updated", {})

    assert "Could not handle the socket event user_updated." in caplog.text


async def test_the_library_and_episode_events_are_subscribed() -> None:
    """Abs sends these, see its LibraryController.js and PodcastManager.js."""
    socket_io = await _socket(_session_config(access_token="access1"))

    assert {
        "episode_added",
        "library_added",
        "library_updated",
        "library_removed",
    } <= socket_io.handlers.keys()


async def test_an_accepted_api_key_is_left_alone() -> None:
    """Abs accepts api keys on the socket after v2.36.1, so nothing is rejected."""
    socket_io = await _socket(_session_config(token="api_key"))

    await socket_io.trigger("init", {})

    assert socket_io.auth_tokens == ["api_key"]
    assert socket_io.disconnects == 0


async def test_a_caller_can_ask_socketio_to_keep_trying() -> None:
    """A server which is briefly unreachable must not have to fail the setup."""
    with patch("socketio.AsyncClient", FakeSocketIoClient):
        socket_client = SocketClient(session_config=_session_config(access_token="access1"))
    await socket_client.init_client(retry=True, wait_timeout=30)

    assert isinstance(socket_client.client, FakeSocketIoClient)
    assert socket_client.client.options == {"retry": True, "wait_timeout": 30}
