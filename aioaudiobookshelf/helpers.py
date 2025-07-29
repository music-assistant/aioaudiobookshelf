"""Helpers for aioaudiobookshelf."""

import base64
import urllib.parse
from enum import StrEnum
from typing import TYPE_CHECKING

from aiohttp.client_exceptions import ClientResponseError, InvalidUrlClientError

from aioaudiobookshelf.exceptions import LoginError
from aioaudiobookshelf.schema.calls_login import LoginParameters, LoginResponse

if TYPE_CHECKING:
    from aioaudiobookshelf.client.session_configuration import SessionConfiguration


class FilterGroup(StrEnum):
    """FilterGroup."""

    GENRES = "genres"
    TAGS = "tags"
    SERIES = "series"
    AUTHORS = "authors"
    PROGRESS = "progress"
    NARRATORS = "narrators"
    MISSING = "missing"
    LANGUAGES = "languages"
    TRACKS = "tracks"


class FilterProgressType(StrEnum):
    """FilterProgressType."""

    FINISHED = "finished"
    NOTSTARTED = "not-started"
    NOTFINISHED = "not-finished"
    INPROGRESS = "in-progress"


def get_library_filter_string(
    *, filter_group: FilterGroup, filter_value: str | FilterProgressType
) -> str:
    """Obtain a string usable as filter_str.

    Currently only narrators, genre, tags, languages and progress.
    """
    if filter_group in [
        FilterGroup.NARRATORS,
        FilterGroup.GENRES,
        FilterGroup.TAGS,
        FilterGroup.LANGUAGES,
    ]:
        _encoded = urllib.parse.quote(base64.b64encode(filter_value.encode()))
        return f"{filter_group.value}.{_encoded}"

    if filter_group == FilterGroup.PROGRESS:
        if filter_value not in FilterProgressType:
            raise RuntimeError("Filter value not acceptable for progress.")
        filter_value = (
            filter_value.value if isinstance(filter_value, FilterProgressType) else filter_value
        )
        _encoded = urllib.parse.quote(base64.b64encode(filter_value.encode()))
        return f"{filter_group.value}.{_encoded}"

    raise NotImplementedError(f"The {filter_group=} is not yet implemented.")


async def get_login_response(
    *, session_config: "SessionConfiguration", username: str, password: str
) -> LoginResponse:
    """Login via username and password."""
    login_request = LoginParameters(username=username, password=password).to_dict()

    try:
        resp = await session_config.session.post(
            f"{session_config.url}/login",
            json=login_request,
            ssl=session_config.verify_ssl,
            raise_for_status=True,
            # adapt > v2.26.0 https://github.com/advplyr/audiobookshelf/discussions/4460
            headers={"x-return-tokens": "true"},
        )
    except (ClientResponseError, InvalidUrlClientError) as exc:
        raise LoginError from exc
    return LoginResponse.from_json(await resp.read())
