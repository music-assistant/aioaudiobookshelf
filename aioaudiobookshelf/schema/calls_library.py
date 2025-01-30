"""Calls for Libraries."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

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
class _LibraryItemsResponseBase(_BaseModel):
    """Due to options of this API call, some parameters omitted."""

    total: int
    limit: int
    page: int


@dataclass
class LibraryItemsMinifiedResponse(_LibraryItemsResponseBase):
    """LibraryItemsMinifiedResponse."""

    results: list[LibraryItemMinified]


@dataclass
class LibraryItemsResponse(_LibraryItemsResponseBase):
    """LibraryItemsResponse."""

    results: list[LibraryItem]
