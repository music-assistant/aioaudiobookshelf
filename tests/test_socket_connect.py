"""The socket client against a real socket.io server."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any
from unittest.mock import Mock

import pytest
import socketio
from aiohttp import web
from aiohttp.test_utils import TestServer

from aioaudiobookshelf.client import SocketClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration


@pytest.mark.parametrize("base_path", ["", "/abs"])
async def test_socket_reaches_abs_behind_a_base_path(
    base_path: str, aiohttp_server: Callable[[web.Application], Awaitable[TestServer]]
) -> None:
    """Abs serves a socket per base path, see its SocketAuthority.js, and we have to hit ours."""
    server = socketio.AsyncServer(async_mode="aiohttp")
    authenticated: asyncio.Future[str] = asyncio.get_running_loop().create_future()

    @server.on("auth")  # type: ignore[misc]
    async def _auth(_sid: str, token: Any) -> None:
        authenticated.set_result(token)

    app = web.Application()
    server.attach(app, socketio_path=f"{base_path}/socket.io")
    test_server = await aiohttp_server(app)

    socket_client = SocketClient(
        session_config=SessionConfiguration(
            session=Mock(),
            url=f"http://127.0.0.1:{test_server.port}{base_path}",
            access_token="access1",
        )
    )
    await socket_client.init_client()
    try:
        assert await asyncio.wait_for(authenticated, timeout=10) == "access1"
    finally:
        await socket_client.shutdown()
