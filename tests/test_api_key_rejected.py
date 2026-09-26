"""Tests for a token abs rejects which cannot be refreshed."""

import logging
from collections.abc import Awaitable, Callable
from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp.client_exceptions import ClientResponseError

from aioaudiobookshelf.client import UserClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import (
    AccessTokenExpiredError,
    TokenIsMissingError,
    TokenNotRenewableError,
)


def _client(**kwargs: str) -> UserClient:
    error = ClientResponseError(request_info=Mock(), history=(), status=401)
    response = Mock(status=401, content_type="application/json", read=AsyncMock(return_value=b""))
    client = UserClient.__new__(UserClient)
    client.session_config = SessionConfiguration(
        session=Mock(
            get=AsyncMock(return_value=response),
            post=AsyncMock(side_effect=error),
            patch=AsyncMock(side_effect=error),
            delete=AsyncMock(side_effect=error),
        ),
        url="http://abs.local",
        **kwargs,
    )
    client.logger = logging.getLogger(__name__)
    return client


def _get(client: UserClient) -> Awaitable[object]:
    return client.get_author_image(author_id="author1")


def _post(client: UserClient) -> Awaitable[object]:
    return client.create_playlist_from_collection(collection_id="collection1")


def _patch(client: UserClient) -> Awaitable[object]:
    return client.update_my_media_progress(
        item_id="item1", duration_seconds=100, progress_seconds=10, is_finished=True
    )


def _delete(client: UserClient) -> Awaitable[object]:
    return client.remove_my_media_progress(media_progress_id="progress1")


@pytest.mark.parametrize("call", [_get, _post, _patch, _delete])
# an api key and a pre v2.26 token both live in token, an access token can stand alone
@pytest.mark.parametrize("session", [{"token": "api_key"}, {"access_token": "access1"}])
async def test_a_rejected_token_without_a_refresh_token(
    call: Callable[[UserClient], Awaitable[object]], session: dict[str, str]
) -> None:
    """Abs deactivates an expired api key, and there is nothing to renew it with."""
    with pytest.raises(TokenNotRenewableError) as excinfo:
        await call(_client(**session))

    assert not isinstance(excinfo.value, TokenIsMissingError)
    assert "cannot be refreshed" in str(excinfo.value)


@pytest.mark.parametrize("call", [_get, _post, _patch, _delete])
async def test_a_rejected_token_which_could_be_refreshed(
    call: Callable[[UserClient], Awaitable[object]],
) -> None:
    """With a refresh token to hand, a 401 is the ordinary expired access token again."""
    client = _client(access_token="access1", refresh_token="refresh1")
    client.session_config.auto_refresh = False

    with pytest.raises(AccessTokenExpiredError):
        await call(client)
