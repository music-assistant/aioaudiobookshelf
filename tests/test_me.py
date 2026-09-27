"""Tests for /api/me calls."""

import logging
from typing import Any
from unittest.mock import AsyncMock, Mock

from aioaudiobookshelf.client.me import MeClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration


class FakeSession:
    """Stands in for the aiohttp session and records the progress updates."""

    def __init__(self) -> None:
        """Init."""
        self.payloads: list[dict[str, Any]] = []

    async def patch(self, _url: str, json: dict[str, Any], **_: Any) -> Mock:
        """Accept a progress update."""
        self.payloads.append(json)
        return Mock(status=200, content_type="application/json", read=AsyncMock(return_value=b""))


def _client(session: FakeSession) -> MeClient:
    client = MeClient.__new__(MeClient)
    client.session_config = SessionConfiguration(
        session=session,  # type: ignore[arg-type]
        url="http://abs.local",
        access_token="access1",
    )
    client.logger = logging.getLogger(__name__)
    return client


async def test_progress_without_duration() -> None:
    """An episode abs has no duration for stores its position, and no bogus duration."""
    session = FakeSession()

    await _client(session).update_my_media_progress(
        item_id="item1",
        episode_id="episode1",
        duration_seconds=0,
        progress_seconds=120,
        is_finished=False,
    )

    assert session.payloads == [{"isFinished": False}, {"currentTime": 120}]


async def test_progress_with_duration() -> None:
    """A known duration is sent as a percentage and as the position."""
    session = FakeSession()

    await _client(session).update_my_media_progress(
        item_id="item1", duration_seconds=400, progress_seconds=100, is_finished=False
    )

    assert session.payloads == [
        {"isFinished": False},
        {"progress": 0.25},
        {"duration": 400, "currentTime": 100},
    ]


async def test_finished_item_sends_no_progress() -> None:
    """Marking an item finished leaves its position to abs."""
    session = FakeSession()

    await _client(session).update_my_media_progress(
        item_id="item1", duration_seconds=0, progress_seconds=0, is_finished=True
    )

    assert session.payloads == [{"isFinished": True}]


class FakeGetSession:
    """Answers a GET and records what was asked for."""

    def __init__(self) -> None:
        """Init."""
        self.url: str | None = None
        self.params: dict[str, Any] | None = None

    async def get(self, url: str, params: dict[str, Any], **_: Any) -> Mock:
        """Answer with an empty list of items."""
        self.url = url
        self.params = params
        return Mock(
            status=200,
            content_type="application/json",
            read=AsyncMock(return_value=b'{"libraryItems": []}'),
        )


async def test_items_in_progress_asks_abs_for_its_own_limit() -> None:
    """Abs falls back to 25 when the limit is not a number, so it has to be sent as one."""
    session = FakeGetSession()

    assert await _client(session).get_my_items_in_progress(limit=5) == []  # type: ignore[arg-type]

    assert session.url is not None
    assert session.url.endswith("/api/me/items-in-progress")
    assert session.params == {"limit": 5}
