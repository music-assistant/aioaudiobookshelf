"""Helpers for aioaudiobookshelf."""

import base64
import urllib.parse
from enum import StrEnum


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
