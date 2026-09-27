"""Tests for /api/libraries calls."""

import json
import logging
from typing import Any
from unittest.mock import AsyncMock, Mock

from aioaudiobookshelf.client.libraries import LibrariesClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration


class FakeSession:
    """Answers with abs' paging counts and records every page asked for."""

    def __init__(self, *, total: int, limit: int) -> None:
        """Init."""
        self.total = total
        self.limit = limit
        self.pages: list[int] = []

    async def get(self, _url: str, params: dict[str, Any], **_: Any) -> Mock:
        """Answer one page. The items themselves do not matter here."""
        self.pages.append(int(params["page"]))
        body = {"total": self.total, "limit": self.limit, "page": params["page"], "results": []}
        return Mock(
            status=200,
            content_type="application/json",
            read=AsyncMock(return_value=json.dumps(body).encode()),
        )


def _client(session: FakeSession) -> LibrariesClient:
    client = LibrariesClient.__new__(LibrariesClient)
    client.session_config = SessionConfiguration(
        session=session,  # type: ignore[arg-type]
        url="http://abs.local",
        access_token="access1",
        pagination_items_per_page=session.limit,
    )
    client.logger = logging.getLogger(__name__)
    return client


async def test_paging_stops_after_the_last_page() -> None:
    """The generator has to end on its own, not only when a caller breaks out of it."""
    session = FakeSession(total=5, limit=2)

    async for _ in _client(session).get_library_items(library_id="library1"):
        pass

    assert session.pages == [0, 1, 2]


async def test_an_unpaged_answer_is_one_page() -> None:
    """Abs sends everything at once and reports limit 0 when it ignored the paging."""
    session = FakeSession(total=5, limit=0)

    async for _ in _client(session).get_library_items(library_id="library1"):
        pass

    assert session.pages == [0]
