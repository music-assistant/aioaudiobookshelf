"""Params and responses for playlists."""

from dataclasses import dataclass

from aioaudiobookshelf.schema.playlist import PlaylistExpanded

from . import _BaseModel


@dataclass
class AllPlaylistsResponse(_BaseModel):
    """AllPlaylistsResponse."""

    playlists: list[PlaylistExpanded]
