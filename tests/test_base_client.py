"""Tests for how the base client maps abs' http errors."""

import logging
from collections.abc import Awaitable, Callable
from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp.client_exceptions import ClientResponseError

from aioaudiobookshelf.client import UserClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import (
    AccessTokenExpiredError,
    ApiError,
    NotFoundError,
)


def _client(status: int) -> UserClient:
    error = ClientResponseError(request_info=Mock(), history=(), status=status)
    client = UserClient.__new__(UserClient)
    client.session_config = SessionConfiguration(
        session=Mock(
            post=AsyncMock(side_effect=error),
            patch=AsyncMock(side_effect=error),
            delete=AsyncMock(side_effect=error),
        ),
        url="http://abs.local",
        access_token="access1",
        # without one a 401 is not an expired access token, see test_api_key_rejected
        refresh_token="refresh1",
        auto_refresh=False,
    )
    client.logger = logging.getLogger(__name__)
    return client


def _post(client: UserClient) -> Awaitable[object]:
    return client.create_playlist_from_collection(collection_id="collection1")


def _patch(client: UserClient) -> Awaitable[object]:
    return client.update_my_media_progress(
        item_id="item1", duration_seconds=100, progress_seconds=10, is_finished=False
    )


def _delete(client: UserClient) -> Awaitable[object]:
    return client.remove_my_media_progress(media_progress_id="progress1")


@pytest.mark.filterwarnings("error::DeprecationWarning")
@pytest.mark.parametrize("call", [_post, _patch, _delete])
@pytest.mark.parametrize(
    ("status", "expected"),
    [(401, AccessTokenExpiredError), (404, NotFoundError), (500, ApiError)],
)
async def test_response_status_is_mapped(
    call: Callable[[UserClient], Awaitable[object]], status: int, expected: type[Exception]
) -> None:
    """Abs' status decides the error, read from a property aiohttp does not deprecate."""
    with pytest.raises(expected):
        await call(_client(status))


async def test_the_url_carries_no_double_slash() -> None:
    """Abs routes /api/..., and //api works only because abs rewrites it."""
    session_config = SessionConfiguration(
        session=Mock(), url="http://abs.local/", access_token="access1"
    )

    assert session_config.url_for("/api/me") == "http://abs.local/api/me"
    assert session_config.url_for("login") == "http://abs.local/login"
