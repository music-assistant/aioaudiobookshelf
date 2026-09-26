"""Our refresh token has to win over one a shared cookie jar holds."""

from collections.abc import AsyncGenerator, Awaitable, Callable
from unittest.mock import Mock, patch

import pytest
from aiohttp import ClientSession, web
from aiohttp.test_utils import TestServer

from aioaudiobookshelf.client import UserClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration

Server = Callable[[web.Application], Awaitable[TestServer]]

# which refresh token abs ended up using, per call
SEEN: list[str | None] = []


def _answer() -> web.Response:
    response = web.json_response({})
    # abs sets the cookie on every answer, for whichever client asked
    response.set_cookie("refresh_token", "another-instance")
    return response


async def _refresh(request: web.Request) -> web.Response:
    # abs' /auth/refresh lets the header override the cookie, see its Auth.js
    SEEN.append(request.headers.get("x-refresh-token") or request.cookies.get("refresh_token"))
    return _answer()


async def _logout(request: web.Request) -> web.Response:
    # abs' /logout prefers the cookie, which is the whole problem
    SEEN.append(request.cookies.get("refresh_token") or request.headers.get("x-refresh-token"))
    return _answer()


@pytest.fixture
async def abs_server(aiohttp_server: Server) -> TestServer:
    """Serve an abs which reports which refresh token it was given."""
    SEEN.clear()
    app = web.Application()
    app.router.add_post("/auth/refresh", _refresh)
    app.router.add_post("/logout", _logout)
    return await aiohttp_server(app)


@pytest.fixture
async def shared_session() -> AsyncGenerator[ClientSession]:
    """Share one session with another client of the same server."""
    async with ClientSession() as session:
        yield session


def _session_config(server: TestServer, session: ClientSession) -> SessionConfiguration:
    session_config = SessionConfiguration(
        session=session,
        url=f"http://127.0.0.1:{server.port}",
        access_token="access1",
        refresh_token="ours",
    )
    # the other instance logged in first and left its cookie behind
    session.cookie_jar.update_cookies({"refresh_token": "another-instance"})
    return session_config


def _client(session_config: SessionConfiguration) -> UserClient:
    client = UserClient.__new__(UserClient)
    client.session_config = session_config
    return client


async def test_refresh_was_never_at_risk(
    abs_server: TestServer, shared_session: ClientSession
) -> None:
    """Abs lets the header override the cookie here, so only logout ever went wrong."""
    session_config = _session_config(abs_server, shared_session)
    refreshed = Mock(user=Mock(access_token="access2", refresh_token="refresh2"))

    with patch(
        "aioaudiobookshelf.client.session_configuration.RefreshResponse.from_json",
        return_value=refreshed,
    ):
        await session_config.refresh()

    assert SEEN == ["ours"]


async def test_logout_uses_our_token_not_the_jars(
    abs_server: TestServer, shared_session: ClientSession
) -> None:
    """Abs prefers the cookie here, so a stale one would end the other instance's session."""
    await _client(_session_config(abs_server, shared_session)).logout()

    assert SEEN == ["ours"]


async def test_abs_own_cookie_does_not_take_over(
    abs_server: TestServer, shared_session: ClientSession
) -> None:
    """Abs sets the cookie on every answer, which must not change the next call either."""
    client = _client(_session_config(abs_server, shared_session))

    await client.logout()
    await client.logout()

    assert SEEN == ["ours", "ours"]
