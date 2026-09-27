"""Params and responses for me."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from aioaudiobookshelf.schema.session import PlaybackSession
from aioaudiobookshelf.schema.shelf import ShelfLibraryItemMinified

from . import _BaseModel


@dataclass(kw_only=True)
class MeListeningSessionsParameters(_BaseModel):
    """MeListeningSessionsParameters."""

    items_per_page: Annotated[int, Alias("itemsPerPage")] = 10
    page: int = 0


@dataclass(kw_only=True)
class MeListeningSessionsResponse(_BaseModel):
    """MeListeningSessionsResponse."""

    total: int
    num_pages: Annotated[int, Alias("numPages")]
    items_per_page: Annotated[int, Alias("itemsPerPage")]
    sessions: list[PlaybackSession]


@dataclass(kw_only=True)
class ItemsInProgressResponse(_BaseModel):
    """ItemsInProgressResponse.

    Abs sends minified items carrying recentEpisode and progressLastUpdate, the
    same shape its continue-listening shelf uses, see its MeController.js.
    """

    library_items: Annotated[list[ShelfLibraryItemMinified], Alias("libraryItems")]
