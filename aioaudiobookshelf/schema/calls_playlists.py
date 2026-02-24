"""Params and responses for playlists."""

from dataclasses import dataclass, field
from typing import Annotated

from mashumaro.types import Alias

from aioaudiobookshelf.schema.playlist import PlaylistExpanded, PlaylistItem

from . import _BaseModel


@dataclass(kw_only=True)
class AllPlaylistsResponse(_BaseModel):
    """AllPlaylistsResponse."""

    playlists: list[PlaylistExpanded]


@dataclass(kw_only=True)
class UpdatePlaylistParameters(_BaseModel):
    """UpdatePlaylistParameters."""

    name: str
    description: str | None = None
    cover_path: Annotated[str | None, Alias("coverPath")] = None
    items: list[PlaylistItem] = field(default_factory=list)


@dataclass(kw_only=True)
class CreatePlaylistParameters(UpdatePlaylistParameters):
    """CreatePlaylistParameters."""

    library_id: Annotated[str, Alias("libraryId")]


@dataclass(kw_only=True)
class PlaylistItemsBatchParameters(_BaseModel):
    """PlaylistItemsBatchParameters."""

    items: list[PlaylistItem]
