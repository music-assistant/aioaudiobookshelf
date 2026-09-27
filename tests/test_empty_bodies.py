"""Tests for answers which carry no json to decode."""

import logging
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from aioaudiobookshelf.client import UserClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import ApiError
from aioaudiobookshelf.schema.calls_playlists import UpdatePlaylistParameters


class FakeSession:
    """Stands in for the aiohttp session and records what was requested."""

    def __init__(self, *, content_type: str = "application/json", body: bytes = b"{}") -> None:
        """Init."""
        self.content_type = content_type
        self.body = body
        self.requests: list[str] = []

    async def request(self, url: str, **_: Any) -> Mock:
        """Answer a request."""
        self.requests.append(url)
        return Mock(
            status=200, content_type=self.content_type, read=AsyncMock(return_value=self.body)
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


async def test_an_empty_batch_asks_abs_nothing() -> None:
    """Without ids there is nothing to request, and nothing to decode."""
    session = FakeSession()

    assert await _client(session).get_library_item_batch_book(item_ids=[]) == []
    assert session.requests == []


async def test_a_playlist_update_without_json_raises_an_abs_error() -> None:
    """A missing body must not surface as a json error."""
    session = FakeSession(content_type="text/plain", body=b"")

    with pytest.raises(ApiError):
        await _client(session).update_playlist(
            playlist_id="playlist1", parameters=UpdatePlaylistParameters(name="new name")
        )
