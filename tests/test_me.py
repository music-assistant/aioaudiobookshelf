"""Tests for /api/me calls."""

import json
from math import ceil
from typing import Any

from aioaudiobookshelf.client.me import MeClient

from .helpers import RecordingSession, make_client


async def test_progress_without_duration() -> None:
    """An episode abs has no duration for stores its position, and no bogus duration."""
    session = RecordingSession()

    await make_client(MeClient, session).update_my_media_progress(
        item_id="item1",
        episode_id="episode1",
        duration_seconds=0,
        progress_seconds=120,
        is_finished=False,
    )

    assert session.payloads == [{"isFinished": False}, {"currentTime": 120}]


async def test_progress_with_duration() -> None:
    """A known duration is sent as a percentage and as the position."""
    session = RecordingSession()

    await make_client(MeClient, session).update_my_media_progress(
        item_id="item1", duration_seconds=400, progress_seconds=100, is_finished=False
    )

    assert session.payloads == [
        {"isFinished": False},
        {"progress": 0.25},
        {"duration": 400, "currentTime": 100},
    ]


async def test_finished_item_sends_no_progress() -> None:
    """Marking an item finished leaves its position to abs."""
    session = RecordingSession()

    await make_client(MeClient, session).update_my_media_progress(
        item_id="item1", duration_seconds=0, progress_seconds=0, is_finished=True
    )

    assert session.payloads == [{"isFinished": True}]


async def test_items_in_progress_asks_abs_for_its_own_limit() -> None:
    """Abs falls back to 25 when the limit is not a number, so it has to be sent as one."""
    session = RecordingSession(body=b'{"libraryItems": []}')

    assert await make_client(MeClient, session).get_my_items_in_progress(limit=5) == []

    assert session.urls[0].endswith("/api/me/items-in-progress")
    assert session.calls[0].params == {"limit": 5}


def _session_pages(total: int, items_per_page: int) -> Any:
    """Answer with abs' listening session paging counts, the sessions do not matter here."""

    def body(params: Any) -> bytes:
        page = {
            "total": total,
            "numPages": ceil(total / items_per_page) if items_per_page else 0,
            "itemsPerPage": items_per_page,
            "page": params["page"],
            "sessions": [],
        }
        return json.dumps(page).encode()

    return body


async def test_a_migrated_user_without_newer_permissions() -> None:
    """Abs copied v1 permissions as stored, and reads a missing one as false."""
    user = {
        "id": "user1",
        "username": "listener",
        "type": "user",
        "token": "token1",
        "mediaProgress": [],
        "seriesHideFromContinueListening": [],
        "bookmarks": [],
        "isActive": True,
        "isLocked": False,
        "lastSeen": None,
        "createdAt": 1600000000000,
        "permissions": {"download": True, "update": True, "delete": False},
        "librariesAccessible": [],
        "itemTagsSelected": [],
    }
    client = make_client(MeClient, RecordingSession(json.dumps(user).encode()))

    permissions = (await client.get_my_user()).permissions

    assert not any(
        (
            permissions.upload,
            permissions.access_all_libraries,
            permissions.access_all_tags,
            permissions.access_explicit_content,
        )
    )


async def test_a_stored_session_abs_could_not_fully_map() -> None:
    """Abs reads a stored 0 back as null, and migrated or local sessions lack the rest."""
    stored_session = {
        "id": "session1",
        "userId": "user1",
        "libraryId": None,
        "libraryItemId": None,
        "episodeId": None,
        "mediaType": "book",
        "mediaMetadata": None,
        "chapters": [],
        "displayTitle": "",
        "displayAuthor": "",
        "coverPath": None,
        "duration": None,
        "playMethod": 3,
        "mediaPlayer": None,
        "deviceInfo": {},
        "serverVersion": None,
        "date": "2026-10-22",
        "dayOfWeek": "Thursday",
        "timeListening": None,
        "startTime": 0,
        "currentTime": 0,
        "startedAt": 1700000000000,
        "updatedAt": 1700000000000,
    }
    page = {"total": 1, "numPages": 1, "itemsPerPage": 10, "sessions": [stored_session]}
    client = make_client(MeClient, RecordingSession(json.dumps(page).encode()))

    pages = [result async for result in client.get_my_listening_sessions()]

    session = pages[0].sessions[0]
    assert {
        session.library_id,
        session.library_item_id,
        session.media_player,
        session.server_version,
        session.time_listening,
        session.duration,
        session.media_metadata,
    } == {None}


async def test_a_media_progress_abs_could_not_map_to_an_item() -> None:
    """Abs sends extraData.libraryItemId or null, see its models/MediaProgress.js."""
    progress = {
        "id": "progress1",
        "userId": "user1",
        "libraryItemId": None,
        "episodeId": None,
        "mediaItemId": "book1",
        "mediaItemType": "book",
        "duration": 100.0,
        "progress": 0.1,
        "currentTime": 10.0,
        "isFinished": False,
        "hideFromContinueListening": False,
        "lastUpdate": 1700000000000,
        "startedAt": 1700000000000,
        "finishedAt": None,
    }
    client = make_client(MeClient, RecordingSession(json.dumps(progress).encode()))

    media_progress = await client.get_my_media_progress(item_id="item1")

    assert media_progress is not None
    assert media_progress.library_item_id is None


async def test_listening_sessions_paging_stops_after_the_last_page() -> None:
    """The generator has to end on its own, abs keeps answering past the last page."""
    session = RecordingSession(body=_session_pages(total=5, items_per_page=2))
    client = make_client(MeClient, session, access_token="access1", pagination_items_per_page=2)

    async for _ in client.get_my_listening_sessions():
        pass

    assert [int(call.params["page"]) for call in session.calls] == [0, 1, 2]


async def test_listening_sessions_stop_on_a_page_size_of_zero() -> None:
    """A page size of 0 would never reach the total, so it ends after the first page."""
    session = RecordingSession(body=_session_pages(total=5, items_per_page=0))
    client = make_client(MeClient, session, access_token="access1", pagination_items_per_page=0)

    async for _ in client.get_my_listening_sessions():
        pass

    assert [int(call.params["page"]) for call in session.calls] == [0]
