"""Tests for passing a library's mark-as-finished settings to a progress update."""

import logging
from typing import Any
from unittest.mock import AsyncMock, Mock

from aioaudiobookshelf.client.me import MeClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration


class FakeSession:
    """Records the progress updates."""

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


async def test_settings_ride_along_with_the_position() -> None:
    """Abs weighs them against the position it is given, so they belong to that call."""
    session = FakeSession()

    await _client(session).update_my_media_progress(
        item_id="item1",
        duration_seconds=400,
        progress_seconds=396,
        is_finished=False,
        mark_as_finished_time_remaining=30,
        mark_as_finished_percent_complete=95,
    )

    assert session.payloads == [
        {"isFinished": False},
        {"progress": 0.99},
        {
            "duration": 400,
            "currentTime": 396,
            "markAsFinishedTimeRemaining": 30,
            "markAsFinishedPercentComplete": 95,
        },
    ]


async def test_one_setting_alone() -> None:
    """Abs prefers the percentage when it has one, so either may be sent on its own."""
    session = FakeSession()

    await _client(session).update_my_media_progress(
        item_id="item1",
        duration_seconds=400,
        progress_seconds=100,
        is_finished=False,
        mark_as_finished_time_remaining=30,
    )

    assert session.payloads[-1] == {
        "duration": 400,
        "currentTime": 100,
        "markAsFinishedTimeRemaining": 30,
    }


async def test_a_finished_item_is_not_weighed() -> None:
    """Saying an item is finished is not a threshold question."""
    session = FakeSession()

    await _client(session).update_my_media_progress(
        item_id="item1",
        duration_seconds=400,
        progress_seconds=400,
        is_finished=True,
        mark_as_finished_time_remaining=30,
    )

    assert session.payloads == [{"isFinished": True}]
