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
