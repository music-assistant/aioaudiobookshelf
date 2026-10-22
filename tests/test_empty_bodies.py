"""Tests for answers which carry no json to decode."""

import pytest

from aioaudiobookshelf.client import UserClient
from aioaudiobookshelf.exceptions import ApiError
from aioaudiobookshelf.schema.calls_playlists import UpdatePlaylistParameters

from .helpers import RecordingSession, make_client


async def test_an_empty_batch_asks_abs_nothing() -> None:
    """Without ids there is nothing to request, and nothing to decode."""
    session = RecordingSession()

    assert await make_client(UserClient, session).get_library_item_batch_book(item_ids=[]) == []
    assert session.calls == []


async def test_a_playlist_update_without_json_raises_an_abs_error() -> None:
    """A missing body must not surface as a json error."""
    session = RecordingSession(body=b"", content_type="text/plain")

    with pytest.raises(ApiError):
        await make_client(UserClient, session).update_playlist(
            playlist_id="playlist1", parameters=UpdatePlaylistParameters(name="new name")
        )
