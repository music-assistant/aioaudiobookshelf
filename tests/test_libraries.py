"""Tests for /api/libraries calls."""

import json
from collections.abc import AsyncGenerator, Callable
from functools import partial
from math import ceil
from typing import Any

import pytest

from aioaudiobookshelf.client.libraries import LibrariesClient

from .helpers import RecordingSession, make_client


def _pages(total: int, limit: int) -> Any:
    """Answer with abs paging counts. The items themselves do not matter here."""

    def body(params: Any) -> bytes:
        page = {"total": total, "limit": limit, "page": params["page"], "results": []}
        return json.dumps(page).encode()

    return body


def _abs_pages(items: list[dict[str, Any]], *, concatenates: bool) -> Any:
    """Page the way abs' LibraryController.js does for playlists and collections.

    limit and page arrive as query strings, so start + limit concatenates up to
    abs 2.37.1. A fixed abs adds them.
    """

    def body(params: Any) -> bytes:
        limit = str(params["limit"])
        start = int(params["page"]) * int(limit)
        end = int(f"{start}{limit}") if concatenates else start + int(limit)
        page = {
            "results": items[start:end],
            "total": len(items),
            "limit": limit,
            "page": str(params["page"]),
        }
        return json.dumps(page).encode()

    return body


def _asked_pages(session: RecordingSession) -> list[int]:
    return [int(call.params["page"]) for call in session.calls]


def _playlist(idx: int) -> dict[str, Any]:
    return {
        "id": f"playlist{idx}",
        "libraryId": "lib1",
        "name": f"Playlist {idx}",
        "lastUpdate": 1,
        "createdAt": 1,
        "items": [],
    }


def _collection(idx: int) -> dict[str, Any]:
    return {
        "id": f"collection{idx}",
        "libraryId": "lib1",
        "name": f"Collection {idx}",
        "lastUpdate": 1,
        "createdAt": 1,
        "books": [],
    }


def _get_playlists(client: LibrariesClient) -> AsyncGenerator[Any]:
    return client.get_library_playlists(library_id="lib1")


def _get_collections(client: LibrariesClient) -> AsyncGenerator[Any]:
    return client.get_library_collections(library_id="lib1")


@pytest.mark.parametrize(
    ("make_item", "get_items"),
    [(_playlist, _get_playlists), (_collection, _get_collections)],
)
@pytest.mark.parametrize(
    ("abs_pages", "expected_pages"),
    # 1100 items in pages of 10: page 1 of a concatenating abs ends at index 1010
    [
        (partial(_abs_pages, concatenates=True), [0, 1, 101]),
        (partial(_abs_pages, concatenates=False), list(range(ceil(1100 / 10)))),
    ],
)
async def test_every_playlist_and_collection_arrives_once(
    make_item: Callable[[int], dict[str, Any]],
    get_items: Callable[[LibrariesClient], AsyncGenerator[Any]],
    abs_pages: Callable[[list[dict[str, Any]]], Any],
    expected_pages: list[int],
) -> None:
    """Abs up to 2.37.1 sends all items up to str(start) + str(limit) from page 1 on."""
    items = [make_item(idx) for idx in range(1100)]
    session = RecordingSession(body=abs_pages(items))
    client = make_client(
        LibrariesClient, session, access_token="access1", pagination_items_per_page=10
    )

    ids = [item.id_ async for page in get_items(client) for item in page.results]

    assert ids == [item["id"] for item in items]
    assert _asked_pages(session) == expected_pages


async def test_an_unpaged_answer_is_one_page() -> None:
    """Abs sends everything at once and reports limit 0 when it ignored the paging."""
    session = RecordingSession(body=_pages(total=5, limit=0))
    client = make_client(
        LibrariesClient, session, access_token="access1", pagination_items_per_page=0
    )

    async for _ in client.get_library_items(library_id="library1"):
        pass

    assert _asked_pages(session) == [0]
