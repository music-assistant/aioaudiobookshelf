"""Calls to /api/playlists."""

from aioaudiobookshelf.schema.calls_playlists import AllPlaylistsResponse
from aioaudiobookshelf.schema.playlist import PlaylistExpanded

from ._base import BaseClient


class PlaylistsClient(BaseClient):
    """PlaylistsClient."""

    # create playlist

    async def get_all_playlists(self) -> list[PlaylistExpanded]:
        """Get all playlists accessible to user."""
        data = await self._get(endpoint="/api/playlists")
        return AllPlaylistsResponse.from_json(data).playlists

    async def get_playlist(self, *, playlist_id: str) -> PlaylistExpanded:
        """Get a playlist."""
        data = await self._get(endpoint=f"/api/playlists/{playlist_id}")
        return PlaylistExpanded.from_json(data)

    # update
    # delete
    # add item
    # remove item
    # batch add + remove
    # create playlist from collection
