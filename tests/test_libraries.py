"""Tests for /api/libraries calls."""

import json
from typing import Any

from aioaudiobookshelf.client.libraries import LibrariesClient

from .helpers import RecordingSession, make_client


def _pages(total: int, limit: int) -> Any:
    """Answer with abs paging counts. The items themselves do not matter here."""

    def body(params: Any) -> bytes:
        page = {"total": total, "limit": limit, "page": params["page"], "results": []}
        return json.dumps(page).encode()

    return body


def _asked_pages(session: RecordingSession) -> list[int]:
    return [int(call.params["page"]) for call in session.calls]


async def test_paging_stops_after_the_last_page() -> None:
    """The generator has to end on its own, not only when a caller breaks out of it."""
    session = RecordingSession(body=_pages(total=5, limit=2))
    client = make_client(
        LibrariesClient, session, access_token="access1", pagination_items_per_page=2
    )

    async for _ in client.get_library_items(library_id="library1"):
        pass

    assert _asked_pages(session) == [0, 1, 2]


async def test_an_unpaged_answer_is_one_page() -> None:
    """Abs sends everything at once and reports limit 0 when it ignored the paging."""
    session = RecordingSession(body=_pages(total=5, limit=0))
    client = make_client(
        LibrariesClient, session, access_token="access1", pagination_items_per_page=0
    )

    async for _ in client.get_library_items(library_id="library1"):
        pass

    assert _asked_pages(session) == [0]
