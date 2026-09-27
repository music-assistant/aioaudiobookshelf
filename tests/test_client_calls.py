"""What the clients ask abs for.

The answers are not asserted: a payload written by hand only proves what we
assumed. The request is ours, so that is what these pin.
"""

import logging
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from aioaudiobookshelf.client import UserClient
from aioaudiobookshelf.client.authors import AuthorImageFormat
from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import SchemaError
from aioaudiobookshelf.schema.calls_authors import AuthorWithItems, AuthorWithItemsAndSeries
from aioaudiobookshelf.schema.playlist import PlaylistItem


class FakeSession:
    """Answers anything with an empty object, and records what was asked."""

    def __init__(self, body: bytes = b"{}") -> None:
        """Init."""
        self.body = body
        self.urls: list[str] = []
        self.params: list[Any] = []

    async def request(self, url: str, params: Any = None, **_: Any) -> Mock:
        """Answer a request."""
        self.urls.append(url)
        self.params.append(params)
        return Mock(
            status=200, content_type="application/json", read=AsyncMock(return_value=self.body)
        )

    get = post = patch = delete = request


def _client(session: FakeSession) -> UserClient:
    client = UserClient.__new__(UserClient)
    client.session_config = SessionConfiguration(
        session=session,  # type: ignore[arg-type]
        url="http://abs.local",
        access_token="access1",
    )
    client.logger = logging.getLogger(__name__)
    return client


async def test_an_item_is_asked_for_by_id() -> None:
    """Abs takes expanded as a query parameter, not as a path."""
    session = FakeSession(b'{"id": "item1"}')

    with pytest.raises(SchemaError, match="LibraryItemExpandedBook"):
        await _client(session).get_library_item_book(book_id="item1", expanded=True)

    assert session.urls == ["http://abs.local/api/items/item1?expanded=1"]


async def test_a_podcast_episode_is_asked_for_below_its_podcast() -> None:
    """Abs nests an episode under the podcast it belongs to."""
    session = FakeSession()

    with pytest.raises(SchemaError, match="PodcastEpisode"):
        await _client(session).get_podcast_episode(podcast_id="pod1", episode_id="ep1")

    assert session.urls == ["http://abs.local/api/podcasts/pod1/episode/ep1"]


async def test_collections_are_read_from_the_account() -> None:
    """A collection list is not per library, unlike the library's own."""
    session = FakeSession(b'{"collections": []}')

    assert await _client(session).get_all_collections() == []
    assert session.urls == ["http://abs.local/api/collections"]


async def test_series_progress_is_asked_for_by_query() -> None:
    """Abs decides what a series answer holds from the include parameter."""
    session = FakeSession()

    with pytest.raises(SchemaError, match="SeriesWithProgress"):
        await _client(session).get_series(series_id="series1", include_progress=True)

    assert session.urls == ["http://abs.local/api/series/series1?include=progress"]


@pytest.mark.parametrize(
    ("kwargs", "expected_query", "expected_model"),
    [
        ({}, "", "Author"),
        ({"include_items": True}, "?include=items", AuthorWithItems.__name__),
        ({"include_series": True}, "?include=items,series", AuthorWithItemsAndSeries.__name__),
    ],
)
async def test_an_author_include_builds_one_query(
    kwargs: dict[str, bool], expected_query: str, expected_model: str
) -> None:
    """Series always includes items, and both go into a single include."""
    session = FakeSession()

    with pytest.raises(SchemaError, match=expected_model):
        await _client(session).get_author(author_id="author1", **kwargs)

    assert session.urls == [f"http://abs.local/api/authors/author1{expected_query}"]


async def test_an_author_image_is_asked_for_with_its_size() -> None:
    """The image is not json, and abs scales it from the query."""
    session = FakeSession(b"an-image")

    image = await _client(session).get_author_image(
        author_id="author1", width=200, height=100, format_=AuthorImageFormat.WEBP
    )

    assert image == b"an-image"
    assert session.params == [{"width": 200, "format": "webp", "raw": 0, "height": 100}]


@pytest.mark.parametrize(
    ("episode_id", "expected"),
    [
        (None, "http://abs.local/api/playlists/playlist1/item/item1"),
        ("ep1", "http://abs.local/api/playlists/playlist1/item/item1/ep1"),
    ],
)
async def test_removing_a_playlist_item_names_the_episode(
    episode_id: str | None, expected: str
) -> None:
    """A podcast entry is removed by podcast and episode, a book by item alone."""
    session = FakeSession()

    with pytest.raises(SchemaError, match="Playlist"):
        await _client(session).remove_item_from_playlist(
            playlist_id="playlist1",
            item=PlaylistItem(library_item_id="item1", episode_id=episode_id),
        )

    assert session.urls == [expected]
