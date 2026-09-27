"""Tests for how the base client consumes abs' answers."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp.client_exceptions import ClientConnectionError, ClientResponseError

import aioaudiobookshelf
from aioaudiobookshelf.client import UserClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import AbsError, SchemaError, ServiceUnavailableError
from aioaudiobookshelf.schema.calls_session import SyncOpenSessionParameters


class FakeResponse:
    """Stands in for an aiohttp response and remembers whether it was consumed."""

    def __init__(
        self, status: int = 200, content_type: str = "application/json", body: bytes = b"{}"
    ) -> None:
        """Init."""
        self.status = status
        self.content_type = content_type
        self.body = body
        self.reads = 0
        self.released = False

    async def read(self) -> bytes:
        """Read the body."""
        self.reads += 1
        return self.body

    def release(self) -> None:
        """Free the connection without reading."""
        self.released = True

    @property
    def consumed(self) -> bool:
        """Whether the connection was freed, one way or the other."""
        return self.reads > 0 or self.released


class FakeSession:
    """Hands out scripted responses, the way aiohttp would."""

    def __init__(self, *responses: FakeResponse, error: Exception | None = None) -> None:
        """Init."""
        self.queue = list(responses)
        self.error = error
        self.handed_out: list[FakeResponse] = []

    async def request(self, *_: Any, raise_for_status: bool = False, **__: Any) -> FakeResponse:
        """Answer a request."""
        if self.error is not None:
            raise self.error
        response = self.queue.pop(0)
        self.handed_out.append(response)
        if raise_for_status and response.status >= 400:
            # aiohttp frees the connection before it raises
            response.release()
            raise ClientResponseError(request_info=Mock(), history=(), status=response.status)
        return response

    get = post = patch = delete = request


def _client(session: FakeSession, *, auto_refresh: bool = False) -> UserClient:
    client = UserClient.__new__(UserClient)
    client.session_config = SessionConfiguration(
        session=session,  # type: ignore[arg-type]
        url="http://abs.local",
        access_token="access1",
        refresh_token="refresh1",
        auto_refresh=auto_refresh,
    )
    client.session_config.refresh = AsyncMock()  # type: ignore[method-assign]
    client.logger = logging.getLogger(__name__)
    return client


# routes which hand the body straight back, so a schema cannot mask what is tested
def _get(client: UserClient) -> Awaitable[object]:
    return client.get_author_image(author_id="author1")


def _post(client: UserClient) -> Awaitable[object]:
    return client.sync_open_session(
        session_id="session1",
        parameters=SyncOpenSessionParameters(current_time=1.0, time_listened=1.0, duration=2.0),
    )


def _patch(client: UserClient) -> Awaitable[object]:
    return client.update_my_media_progress(
        item_id="item1", duration_seconds=100, progress_seconds=10, is_finished=True
    )


def _delete(client: UserClient) -> Awaitable[object]:
    return client.remove_my_media_progress(media_progress_id="progress1")


VERBS = [_get, _post, _patch, _delete]


@pytest.mark.parametrize("call", VERBS)
@pytest.mark.parametrize("error", [ClientConnectionError(), TimeoutError()])
async def test_connection_errors_become_abs_errors(
    call: Callable[[UserClient], Awaitable[object]], error: Exception
) -> None:
    """An unreachable abs has to look like every other temporary failure."""
    with pytest.raises(ServiceUnavailableError):
        await call(_client(FakeSession(error=error)))


@pytest.mark.parametrize("call", VERBS)
async def test_a_failed_call_frees_its_connection(
    call: Callable[[UserClient], Awaitable[object]],
) -> None:
    """An answer we do not read still has to release its connection."""
    session = FakeSession(FakeResponse(status=500))

    with pytest.raises(AbsError):
        await call(_client(session))

    assert [response.consumed for response in session.handed_out] == [True]


@pytest.mark.parametrize("call", [_patch, _delete])
async def test_an_answer_without_json_frees_its_connection(
    call: Callable[[UserClient], Awaitable[object]],
) -> None:
    """Abs answers some calls with no body at all."""
    session = FakeSession(FakeResponse(content_type="text/plain", body=b""))

    await call(_client(session))

    assert [response.consumed for response in session.handed_out] == [True]


@pytest.mark.parametrize("call", VERBS)
async def test_a_retried_call_frees_both_connections(
    call: Callable[[UserClient], Awaitable[object]],
) -> None:
    """The answer to the first, rejected call must not be left hanging either."""
    session = FakeSession(FakeResponse(status=401), FakeResponse())

    await call(_client(session, auto_refresh=True))

    assert [response.consumed for response in session.handed_out] == [True, True]


async def test_author_image_is_returned() -> None:
    """An image is not json, which used to make every call fail."""
    session = FakeSession(FakeResponse(content_type="image/jpeg", body=b"an-image"))

    image = await _client(session).get_author_image(author_id="author1")

    assert image == b"an-image"


def _login_with_password(session_config: SessionConfiguration) -> Awaitable[object]:
    return aioaudiobookshelf.get_user_client(
        session_config=session_config, username="user", password="password"
    )


def _login_with_token(session_config: SessionConfiguration) -> Awaitable[object]:
    return aioaudiobookshelf.get_user_client_by_token(session_config=session_config)


@pytest.mark.parametrize("error", [ClientConnectionError(), TimeoutError()])
@pytest.mark.parametrize("login", [_login_with_password, _login_with_token])
async def test_an_unreachable_abs_does_not_look_like_a_wrong_password(
    login: Callable[[SessionConfiguration], Awaitable[object]], error: Exception
) -> None:
    """Logging in against a server which is down is not a login failure."""
    session_config = SessionConfiguration(
        session=FakeSession(error=error),  # type: ignore[arg-type]
        url="http://abs.local",
        token="api_key",
    )

    with pytest.raises(ServiceUnavailableError):
        await login(session_config)


async def test_an_answer_that_does_not_fit_the_schema_is_an_abs_error() -> None:
    """A schema gap must reach the caller as one of our errors, not a json one."""
    session = FakeSession(FakeResponse(body=b'{"libraries": [{"nope": 1}]}'))

    with pytest.raises(AbsError) as excinfo:
        await _client(session).get_all_libraries()

    assert isinstance(excinfo.value, SchemaError)
