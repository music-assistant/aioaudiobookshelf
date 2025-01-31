"""Calls for Libraries."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from aioaudiobookshelf.schema.author import AuthorExpanded
from aioaudiobookshelf.schema.collection import Collection, CollectionExpanded
from aioaudiobookshelf.schema.playlist import PlaylistExpanded
from aioaudiobookshelf.schema.series_books import SeriesBooks, SeriesBooksMinified

from . import _BaseModel
from .library import Library, LibraryFilterData, LibraryItem, LibraryItemMinified


@dataclass
class AllLibrariesResponse(_BaseModel):
    """LibrariesResponse."""

    libraries: list[Library]


@dataclass
class LibraryWithFilterDataResponse(_BaseModel):
    """LibraryWithFilterDataResponse."""

    filterdata: LibraryFilterData
    issues: int
    num_user_playlists: Annotated[int, Alias("numUserPlaylists")]
    library: Library


@dataclass
class _LibraryPaginationResponseBase(_BaseModel):
    """Due to options of this API call, some parameters omitted."""

    total: int
    limit: int
    page: int


@dataclass
class LibraryItemsMinifiedResponse(_LibraryPaginationResponseBase):
    """LibraryItemsMinifiedResponse."""

    results: list[LibraryItemMinified]


@dataclass
class LibraryItemsResponse(_LibraryPaginationResponseBase):
    """LibraryItemsResponse."""

    results: list[LibraryItem]


@dataclass
class LibrarySeriesResponse(_LibraryPaginationResponseBase):
    """LibrarySeriesResponse."""

    results: list[SeriesBooks]


@dataclass
class LibrarySeriesMinifiedResponse(_LibraryPaginationResponseBase):
    """LibrarySeriesMinifiedResponse."""

    results: list[SeriesBooksMinified]


@dataclass
class LibraryCollectionsResponse(_LibraryPaginationResponseBase):
    """LibraryCollectionsResponse."""

    results: list[CollectionExpanded]


@dataclass
class LibraryCollectionsMinifiedResponse(_LibraryPaginationResponseBase):
    """LibraryCollectionMinifiedResponse."""

    results: list[Collection]


@dataclass
class LibraryPlaylistsResponse(_LibraryPaginationResponseBase):
    """LibraryPlaylistsResponse."""

    results: list[PlaylistExpanded]


@dataclass
class LibraryAuthorsResponse(_BaseModel):
    """LibraryAuthorsResponse."""

    authors: list[AuthorExpanded]
