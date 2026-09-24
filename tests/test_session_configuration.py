"""Tests for the session configuration."""

import asyncio
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

from aioaudiobookshelf.client.session_configuration import SessionConfiguration


async def test_concurrent_refresh_waits_for_new_token() -> None:
    """A refresh requested during a running refresh returns only once the new token is set."""
    release = asyncio.Event()
    post_calls = 0

    async def post(*_: Any, **__: Any) -> Mock:
        nonlocal post_calls
        post_calls += 1
        await release.wait()
        return Mock(read=AsyncMock(return_value=b""))

    session_config = SessionConfiguration(
        session=Mock(post=post),
        url="http://abs.local",
        access_token="access1",
        refresh_token="refresh1",
    )

    async def refresh() -> str | None:
        await session_config.refresh()
        return session_config.access_token

    refresh_response = Mock(user=Mock(access_token="access2", refresh_token="refresh2"))
    with patch(
        "aioaudiobookshelf.client.session_configuration.RefreshResponse.from_json",
        return_value=refresh_response,
    ):
        first = asyncio.create_task(refresh())
        await asyncio.sleep(0)
        second = asyncio.create_task(refresh())
        await asyncio.sleep(0)
        release.set()
        tokens = await asyncio.gather(first, second)

    assert tokens == ["access2", "access2"]
    assert post_calls == 1
