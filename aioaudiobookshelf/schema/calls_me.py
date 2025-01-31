"""Params and responses for me."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from aioaudiobookshelf.schema.session import PlaybackSession

from . import _BaseModel


@dataclass
class MeListeningSessionsParameters(_BaseModel):
    """MeListeningSessionsParameters."""

    items_per_page: Annotated[int, Alias("itemsPerPage")] = 10
    page: int = 0


@dataclass
class MeListeningSessionsResponse(_BaseModel):
    """MeListeningSessionsResponse."""

    total: int
    num_pages: Annotated[int, Alias("numPages")]
    items_per_page: Annotated[int, Alias("itemsPerPage")]
    sessions: list[PlaybackSession]
