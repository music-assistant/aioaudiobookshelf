"""Tests for the socket client."""

from unittest.mock import AsyncMock, Mock

from aioaudiobookshelf.client import SocketClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import RefreshTokenExpiredError


async def _get_socket_client(session_config: SessionConfiguration) -> SocketClient:
    socket_client = SocketClient(session_config=session_config)
    socket_client.client.connect = AsyncMock()  # type: ignore[method-assign]
    socket_client.client.emit = AsyncMock()  # type: ignore[method-assign]
    socket_client.client.disconnect = AsyncMock()  # type: ignore[method-assign]
    await socket_client.init_client()
    await socket_client.client._trigger_event("connect", "/")
    return socket_client


async def _auth_failed(socket_client: SocketClient) -> None:
    await socket_client.client._trigger_event("auth_failed", "/", {"message": "Invalid token"})


def _session_config(**kwargs: str) -> SessionConfiguration:
    return SessionConfiguration(session=Mock(), url="http://abs.local", **kwargs)


def _emitted_tokens(socket_client: SocketClient) -> list[str]:
    emit = socket_client.client.emit
    assert isinstance(emit, AsyncMock)
    return [call.kwargs["data"] for call in emit.call_args_list if call.kwargs["event"] == "auth"]


async def test_expired_access_token_refreshed_on_auth_failed() -> None:
    """An access token rejected by the socket is refreshed and sent again."""
    session_config = _session_config(access_token="access1", refresh_token="refresh1")

    async def refresh() -> None:
        session_config.access_token = "access2"

    session_config.refresh = AsyncMock(side_effect=refresh)  # type: ignore[method-assign]
    socket_client = await _get_socket_client(session_config)

    await _auth_failed(socket_client)

    assert _emitted_tokens(socket_client) == ["access1", "access2"]


async def test_auth_retried_once_per_connection() -> None:
    """A second auth failure on the same connection does not refresh again."""
    session_config = _session_config(access_token="access1", refresh_token="refresh1")
    refresh = AsyncMock()
    session_config.refresh = refresh  # type: ignore[method-assign]
    socket_client = await _get_socket_client(session_config)

    await _auth_failed(socket_client)
    await _auth_failed(socket_client)

    refresh.assert_awaited_once()


async def test_expired_refresh_token_calls_callback() -> None:
    """An expired refresh token triggers the callback, then authenticates with its tokens."""
    session_config = _session_config(access_token="access1", refresh_token="refresh1")
    session_config.refresh = AsyncMock(side_effect=RefreshTokenExpiredError)  # type: ignore[method-assign]
    socket_client = await _get_socket_client(session_config)

    async def on_refresh_token_expired() -> None:
        session_config.access_token = "access2"

    socket_client.set_refresh_token_expired_callback(
        on_refresh_token_expired=on_refresh_token_expired
    )

    await _auth_failed(socket_client)

    assert _emitted_tokens(socket_client) == ["access1", "access2"]


async def test_api_key_auth_failed_disconnects() -> None:
    """A rejected api key disconnects the socket, as abs does not support it."""
    socket_client = await _get_socket_client(_session_config(token="api_key"))

    await _auth_failed(socket_client)

    disconnect = socket_client.client.disconnect
    assert isinstance(disconnect, AsyncMock)
    disconnect.assert_awaited_once()
