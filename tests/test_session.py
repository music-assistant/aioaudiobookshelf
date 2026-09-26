"""Tests for /api/session calls."""

import logging
from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp.client_exceptions import ClientResponseError

from aioaudiobookshelf.client.session import SessionClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import (
    ApiError,
    SessionNotFoundError,
    SessionSyncError,
    SessionSyncNotFoundError,
)
from aioaudiobookshelf.schema.calls_session import SyncOpenSessionParameters


def _client(status: int) -> SessionClient:
    error = ClientResponseError(request_info=Mock(), history=(), status=status)
    client = SessionClient.__new__(SessionClient)
    client.session_config = SessionConfiguration(
        session=Mock(post=AsyncMock(side_effect=error)),
        url="http://abs.local",
        access_token="access1",
    )
    client.logger = logging.getLogger(__name__)
    return client


async def _sync(client: SessionClient) -> None:
    await client.sync_open_session(
        session_id="session1",
        parameters=SyncOpenSessionParameters(current_time=1.0, time_listened=1.0, duration=2.0),
    )


@pytest.mark.parametrize(
    "expected", [SessionSyncNotFoundError, SessionSyncError, SessionNotFoundError]
)
async def test_sync_of_a_gone_session(expected: type[Exception]) -> None:
    """A session abs no longer has is reported as both, so either catch keeps working."""
    with pytest.raises(expected):
        await _sync(_client(404))


async def test_sync_failure_is_not_a_missing_session() -> None:
    """A failing sync of an existing session stays a plain sync error."""
    with pytest.raises(SessionSyncError) as excinfo:
        await _sync(_client(500))

    assert not isinstance(excinfo.value, SessionNotFoundError)


async def test_closing_a_gone_session() -> None:
    """Closing a session abs no longer has says so."""
    with pytest.raises(SessionNotFoundError):
        await _client(404).close_open_session(session_id="session1")


async def test_failing_close_is_not_a_missing_session() -> None:
    """A close which failed for another reason is not reported as a missing session."""
    with pytest.raises(ApiError) as excinfo:
        await _client(500).close_open_session(session_id="session1")

    assert not isinstance(excinfo.value, SessionNotFoundError)
