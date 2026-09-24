"""Tests for library calls."""

import json
from collections.abc import AsyncGenerator, Callable
from typing import Any
from unittest.mock import Mock

import pytest

from aioaudiobookshelf.client.libraries import LibrariesClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration


def _abs_paginate(items: list[dict[str, Any]], params: dict[str, Any]) -> bytes:
    # LibraryController.js: limit and page are query strings, so start + limit concatenates
    limit = str(params["limit"]) if "limit" in params else ""
    page = int(params.get("page", 0))
    results = items
    if limit:
        start = page * int(limit)
        results = items[start : int(f"{start}{limit}")]
    return json.dumps(
        {"results": results, "total": len(items), "limit": limit or 0, "page": page}
    ).encode()


def _client(items: list[dict[str, Any]]) -> LibrariesClient:
    client = LibrariesClient.__new__(LibrariesClient)
    client.session_config = SessionConfiguration(
        session=Mock(), url="http://abs.local", pagination_items_per_page=30
    )

    async def get(_endpoint: str, params: dict[str, Any]) -> bytes:
        return _abs_paginate(items, params)

    client._get = get  # type: ignore[method-assign]
    return client


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
async def test_items_returned_once(
    make_item: Callable[[int], dict[str, Any]],
    get_items: Callable[[LibrariesClient], AsyncGenerator[Any]],
) -> None:
    """Every playlist and collection is returned exactly once."""
    items = [make_item(idx) for idx in range(100)]
    ids = []
    async for response in get_items(_client(items)):
        if not response.results:
            break
        ids.extend(x.id_ for x in response.results)

    assert ids == [x["id"] for x in items]
