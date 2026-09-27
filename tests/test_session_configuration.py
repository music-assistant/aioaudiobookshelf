"""Tests for the session configuration."""

import asyncio
from collections.abc import AsyncGenerator, Callable, Coroutine
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from aiohttp.client_exceptions import ClientResponseError

from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import ApiError, RefreshTokenExpiredError


class FakeSession:
    """Stands in for the aiohttp session on /auth/refresh."""

    def __init__(self, error: Exception | None = None) -> None:
        """Init."""
        self.error = error
        self.calls = 0
        self.release = asyncio.Event()

    async def post(self, *_: Any, **__: Any) -> Mock:
        """Answer a refresh, once released."""
        self.calls += 1
        await self.release.wait()
        if self.error is not None:
            raise self.error
        return Mock(read=AsyncMock(return_value=b""))


@pytest.fixture
async def refreshed_tokens() -> AsyncGenerator[None]:
    """Let a refresh return the next token pair."""
    response = Mock(user=Mock(access_token="access2", refresh_token="refresh2"))
    with patch(
        "aioaudiobookshelf.client.session_configuration.RefreshResponse.from_json",
        return_value=response,
    ):
        yield


def _session_config(session: FakeSession) -> SessionConfiguration:
    return SessionConfiguration(
        session=session,  # type: ignore[arg-type]
        url="http://abs.local",
        access_token="access1",
        refresh_token="refresh1",
    )


async def _gather_refreshes(
    session: FakeSession, refresh: Callable[[], Coroutine[Any, Any, Any]]
) -> list[Any]:
    """Start two concurrent refreshes, release the request, and collect their outcomes."""
    tasks = []
    for _ in range(2):
        tasks.append(asyncio.create_task(refresh()))
        await asyncio.sleep(0)
    session.release.set()
    return await asyncio.gather(*tasks, return_exceptions=True)


@pytest.mark.usefixtures("refreshed_tokens")
async def test_concurrent_refresh_waits_for_new_token() -> None:
    """A refresh requested during a running refresh returns only once the new token is set."""
    session = FakeSession()
    session_config = _session_config(session)

    async def refresh() -> str | None:
        await session_config.refresh()
        return session_config.access_token

    tokens = await _gather_refreshes(session, refresh)

    assert tokens == ["access2", "access2"]
    assert session.calls == 1


async def test_concurrent_refresh_shares_a_failure() -> None:
    """A failed refresh is reported to the waiting callers without asking abs again."""
    session = FakeSession(ClientResponseError(Mock(), (), status=401))
    session_config = _session_config(session)

    results = await _gather_refreshes(session, session_config.refresh)

    assert [type(x) for x in results] == [RefreshTokenExpiredError, RefreshTokenExpiredError]
    assert session.calls == 1


@pytest.mark.usefixtures("refreshed_tokens")
async def test_refresh_retried_after_a_failure() -> None:
    """A failure is not remembered for callers which arrive afterwards."""
    session = FakeSession(ClientResponseError(Mock(), (), status=401))
    session_config = _session_config(session)
    session.release.set()

    with pytest.raises(RefreshTokenExpiredError):
        await session_config.refresh()

    session.error = None
    await session_config.refresh()

    assert session_config.access_token == "access2"
    assert session.calls == 2


async def test_concurrent_login_ends_a_queued_refresh() -> None:
    """A refresh waiting behind a login uses its tokens instead of refreshing."""
    session = FakeSession()
    session_config = _session_config(session)
    login_response = Mock(user=Mock(access_token="access3", refresh_token="refresh3"))

    async def get_login_response(**_: Any) -> Mock:
        await session.release.wait()
        return login_response

    with patch(
        "aioaudiobookshelf.client.session_configuration.get_login_response", get_login_response
    ):
        login = asyncio.create_task(
            session_config.authenticate(username="user", password="password")
        )
        await asyncio.sleep(0)
        refresh = asyncio.create_task(session_config.refresh())
        await asyncio.sleep(0)
        session.release.set()
        await asyncio.gather(login, refresh)

    assert session_config.access_token == "access3"
    assert session.calls == 0


async def test_the_access_token_is_the_one_sent() -> None:
    """BaseClient.token already prefers it, so the requests have to use the same one."""
    session_config = SessionConfiguration(
        session=Mock(), url="http://abs.local", token="old", access_token="access1"
    )

    assert session_config.headers == {"Authorization": "Bearer access1"}


async def test_a_relogin_drops_the_token_it_replaced() -> None:
    """A server which starts issuing access tokens no longer accepts the old one."""
    session_config = SessionConfiguration(
        session=Mock(), url="http://abs.local", token="old", refresh_token="refresh1"
    )
    login_response = Mock(user=Mock(access_token="access3", refresh_token="refresh3"))

    with patch(
        "aioaudiobookshelf.client.session_configuration.get_login_response",
        AsyncMock(return_value=login_response),
    ):
        await session_config.authenticate(username="user", password="password")

    assert session_config.token is None


async def test_an_unreadable_refresh_answer_is_an_abs_error() -> None:
    """Whatever abs answered with, the caller has to see one of our errors."""
    session = FakeSession()
    session.release.set()

    with pytest.raises(ApiError):
        await _session_config(session).refresh()
