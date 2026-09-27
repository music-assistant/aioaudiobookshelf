"""What more than one test needs.

Only the parts that are the same everywhere live here. A fake which models
something a test is about — a scripted answer queue, a blocking request —
belongs in that test, not in a shared one with a flag per caller.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar
from unittest.mock import AsyncMock, Mock

from aioaudiobookshelf.client._base import BaseClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration

URL = "http://abs.local"

ClientT = TypeVar("ClientT", bound=BaseClient)


def make_client(client_cls: type[ClientT], session: Any, **config: Any) -> ClientT:
    """Build a client around a fake session, without logging in first.

    Given no token it gets an access token, which is what most tests want.
    """
    config = config or {"access_token": "access1"}
    client = client_cls.__new__(client_cls)
    client.session_config = SessionConfiguration(session=session, url=URL, **config)
    client.logger = logging.getLogger("tests")
    return client


def json_response(
    body: bytes = b"{}", *, status: int = 200, content_type: str = "application/json"
) -> Mock:
    """Build an answer shaped like the aiohttp response the client reads."""
    return Mock(status=status, content_type=content_type, read=AsyncMock(return_value=body))


def _copy(value: Any) -> Any:
    return dict(value) if isinstance(value, dict) else value


@dataclass
class Call:
    """One request a client made."""

    url: str
    params: Any = None
    json: Any = None


@dataclass
class RecordingSession:
    """Answers every verb with one body, and remembers what was asked for.

    The body may be a callable, for an answer which depends on the query.
    """

    body: bytes | Callable[[Any], bytes] = b"{}"
    content_type: str = "application/json"
    calls: list[Call] = field(default_factory=list)

    async def request(self, url: str, params: Any = None, json: Any = None, **_: Any) -> Mock:
        """Answer a request."""
        # the client reuses one params dict across pages, so record a copy
        self.calls.append(Call(url=url, params=_copy(params), json=_copy(json)))
        body = self.body(params) if callable(self.body) else self.body
        return json_response(body, content_type=self.content_type)

    get = post = patch = delete = request

    @property
    def urls(self) -> list[str]:
        """The url of every call, in order."""
        return [call.url for call in self.calls]

    @property
    def payloads(self) -> list[Any]:
        """The json body of every call which carried one."""
        return [call.json for call in self.calls if call.json is not None]
