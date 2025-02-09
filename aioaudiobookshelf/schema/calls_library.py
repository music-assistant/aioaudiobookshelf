"""Calls for Libraries."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from aioaudiobookshelf.schema.author import AuthorExpanded, Narrator
from aioaudiobookshelf.schema.collection import Collection, CollectionExpanded
from aioaudiobookshelf.schema.playlist import PlaylistExpanded
from aioaudiobookshelf.schema.series_books import SeriesBooks, SeriesBooksMinified

from . import _BaseModel
from .library import Library, LibraryFilterData, LibraryItem, LibraryItemMinified


@dataclass(kw_only=True)
class AllLibrariesResponse(_BaseModel):
    """LibrariesResponse."""

    libraries: list[Library]


@dataclass(kw_only=True)
class LibraryWithFilterDataResponse(_BaseModel):
    """LibraryWithFilterDataResponse."""

    filterdata: LibraryFilterData
    issues: int
    num_user_playlists: Annotated[int, Alias("numUserPlaylists")]
    library: Library


@dataclass(kw_only=True)
class _LibraryPaginationResponseBase(_BaseModel):
    """Due to options of this API call, some parameters omitted."""

    total: int
    limit: int
    page: int


@dataclass(kw_only=True)
class LibraryItemsMinifiedResponse(_LibraryPaginationResponseBase):
    """LibraryItemsMinifiedResponse."""

    results: list[LibraryItemMinified]


@dataclass(kw_only=True)
class LibraryItemsResponse(_LibraryPaginationResponseBase):
    """LibraryItemsResponse."""

    results: list[LibraryItem]


@dataclass(kw_only=True)
class LibrarySeriesResponse(_LibraryPaginationResponseBase):
    """LibrarySeriesResponse."""

    results: list[SeriesBooks]


@dataclass(kw_only=True)
class LibrarySeriesMinifiedResponse(_LibraryPaginationResponseBase):
    """LibrarySeriesMinifiedResponse."""

    results: list[SeriesBooksMinified]


@dataclass(kw_only=True)
class LibraryCollectionsResponse(_LibraryPaginationResponseBase):
    """LibraryCollectionsResponse."""

    results: list[CollectionExpanded]


@dataclass(kw_only=True)
class LibraryCollectionsMinifiedResponse(_LibraryPaginationResponseBase):
    """LibraryCollectionMinifiedResponse."""

    results: list[Collection]


@dataclass(kw_only=True)
class LibraryPlaylistsResponse(_LibraryPaginationResponseBase):
    """LibraryPlaylistsResponse."""

    results: list[PlaylistExpanded]


@dataclass(kw_only=True)
class LibraryAuthorsResponse(_BaseModel):
    """LibraryAuthorsResponse."""

    authors: list[AuthorExpanded]


@dataclass(kw_only=True)
class LibraryNarratorsResponse(_BaseModel):
    """LibraryNarratorsResponse."""

    narrators: list[Narrator]
