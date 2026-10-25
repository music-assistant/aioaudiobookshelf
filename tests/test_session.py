"""Tests for /api/session calls."""

import json
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp.client_exceptions import ClientResponseError

from aioaudiobookshelf.client.session import SessionClient
from aioaudiobookshelf.exceptions import (
    ApiError,
    SessionNotFoundError,
    SessionSyncError,
    SessionSyncNotFoundError,
)
from aioaudiobookshelf.schema.calls_session import SyncOpenSessionParameters

from .helpers import RecordingSession, make_client


def _client(*statuses: int) -> SessionClient:
    errors = [
        ClientResponseError(request_info=Mock(), history=(), status=status) for status in statuses
    ]
    client = make_client(
        SessionClient,
        Mock(post=AsyncMock(side_effect=errors)),
        access_token="access1",
        refresh_token="refresh1",
    )
    client.session_config.refresh = AsyncMock()  # type: ignore[method-assign]
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


async def test_sync_of_a_gone_session_after_a_refresh() -> None:
    """The call repeated after a token refresh has to keep what abs answered."""
    with pytest.raises(SessionSyncNotFoundError):
        await _sync(_client(401, 404))


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


async def test_local_sessions_abs_could_not_sync_are_named() -> None:
    """Abs answers 200 and reports a failure per session, see its PlaybackSessionManager.js."""
    body = (
        b'{"results": [{"id": "session1", "success": true, "progressSynced": true},'
        b' {"id": "session2", "success": false, "error": "Media item not found"}]}'
    )
    client = make_client(SessionClient, RecordingSession(body))

    with pytest.raises(SessionSyncError, match=r"session2 \(Media item not found\)"):
        await client.sync_local_sessions(playback_sessions=[])


def _open_episode_session(**changes: Any) -> bytes:
    """Build an episode session as abs sends it for one it opened."""
    open_session = {
        "id": "session1",
        "userId": "user1",
        "libraryId": "library1",
        "libraryItemId": "item1",
        "episodeId": "episode1",
        "mediaType": "podcast",
        "mediaMetadata": {"title": "Show 1", "genres": [], "explicit": False},
        "chapters": [],
        "displayTitle": "Episode 1",
        "displayAuthor": "",
        "coverPath": None,
        "duration": 60.0,
        "playMethod": 0,
        "mediaPlayer": "unknown",
        "deviceInfo": {},
        "serverVersion": "2.37.1",
        "date": "2026-10-22",
        "dayOfWeek": "Thursday",
        "timeListening": 0,
        "startTime": 0,
        "currentTime": 0,
        "startedAt": 1700000000000,
        "updatedAt": 1700000000000,
        "audioTracks": [],
    }
    return json.dumps(open_session | changes).encode()


async def test_an_open_episode_session_with_a_chapter_a_client_patched_in() -> None:
    """Abs copies the episode's chapters into the session as stored, see its Podcast.js."""
    body = _open_episode_session(chapters=[{"title": "Intro", "start": 0.5}])
    client = make_client(SessionClient, RecordingSession(body))

    session = await client.get_open_session(session_id="session1")

    assert (session.chapters[0].title, session.chapters[0].end) == ("Intro", None)


async def test_an_open_session_of_an_episode_abs_before_2_7_1_could_not_probe() -> None:
    """Abs copied the audio file's null duration, newer ones send 0 instead."""
    body = _open_episode_session(duration=None, serverVersion="2.6.0")
    client = make_client(SessionClient, RecordingSession(body))

    session = await client.get_open_session(session_id="session1")

    assert session.duration == 0
