"""Calls to /api/playlists."""

from aioaudiobookshelf.schema.calls_playlists import (
    AllPlaylistsResponse,
    CreatePlaylistParameters,
    PlaylistItemsBatchParameters,
    UpdatePlaylistParameters,
)
from aioaudiobookshelf.schema.playlist import PlaylistExpanded, PlaylistItem

from ._base import BaseClient


class PlaylistsClient(BaseClient):
    """PlaylistsClient."""

    async def create_playlist(self, *, parameters: CreatePlaylistParameters) -> PlaylistExpanded:
        """Create a playlist."""
        data = await self._post(endpoint="/api/playlists", data=parameters.to_dict())
        return PlaylistExpanded.from_json(data)

    async def get_all_playlists(self) -> list[PlaylistExpanded]:
        """Get all playlists accessible to user."""
        data = await self._get(endpoint="/api/playlists")
        return AllPlaylistsResponse.from_json(data).playlists

    async def get_playlist(self, *, playlist_id: str) -> PlaylistExpanded:
        """Get a playlist."""
        data = await self._get(endpoint=f"/api/playlists/{playlist_id}")
        return PlaylistExpanded.from_json(data)

    async def update_playlist(
        self, *, playlist_id: str, parameters: UpdatePlaylistParameters
    ) -> PlaylistExpanded:
        """Update playlist."""
        data = await self._patch(
            endpoint=f"/api/playlists/{playlist_id}", data=parameters.to_dict()
        )
        return PlaylistExpanded.from_json(data)

    async def delete_playlist(self, *, playlist_id: str) -> None:
        """Delete playlist."""
        await self._delete(endpoint=f"/api/playlists/{playlist_id}")

    async def add_item_to_playlist(
        self, *, playlist_id: str, item: PlaylistItem
    ) -> PlaylistExpanded:
        """Add item to playlist."""
        data = await self._post(endpoint=f"/api/playlists/{playlist_id}/item", data=item.to_dict())
        return PlaylistExpanded.from_json(data)

    async def remove_item_from_playlist(
        self, *, playlist_id: str, item: PlaylistItem
    ) -> PlaylistExpanded:
        """Remove item from playlist."""
        endpoint = f"/api/playlists/{playlist_id}/item/{item.library_item_id}"
        if item.episode_id is not None:
            endpoint += f"/{item.episode_id}"
        data = await self._delete(endpoint=endpoint)
        return PlaylistExpanded.from_json(data)

    async def add_item_to_playlist_batch(
        self, *, playlist_id: str, items: list[PlaylistItem]
    ) -> PlaylistExpanded:
        """Add multiple items to playlist."""
        parameters = PlaylistItemsBatchParameters(items=items)
        data = await self._post(
            endpoint=f"/api/playlists/{playlist_id}/batch/add", data=parameters.to_dict()
        )
        return PlaylistExpanded.from_json(data)

    async def remove_item_to_playlist_batch(
        self, *, playlist_id: str, items: list[PlaylistItem]
    ) -> PlaylistExpanded:
        """Remove multiple items to playlist."""
        parameters = PlaylistItemsBatchParameters(items=items)
        data = await self._post(
            endpoint=f"/api/playlists/{playlist_id}/batch/remove", data=parameters.to_dict()
        )
        return PlaylistExpanded.from_json(data)

    async def create_playlist_from_collection(self, *, collection_id: str) -> PlaylistExpanded:
        """Create playlist from collection."""
        data = await self._post(endpoint=f"/api/playlists/collection/{collection_id}")
        return PlaylistExpanded.from_json(data)
