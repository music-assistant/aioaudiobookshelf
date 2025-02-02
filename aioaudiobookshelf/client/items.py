"""Calls to /api/items."""

from aioaudiobookshelf.client._base import BaseClient
from aioaudiobookshelf.schema.calls_items import (
    LibraryItemsBatchBookResponse,
    LibraryItemsBatchParameters,
    LibraryItemsBatchPodcastResponse,
    PlaybackSessionParameters,
)
from aioaudiobookshelf.schema.library import (
    LibraryItemBook,
    LibraryItemExpandedBook,
    LibraryItemExpandedPodcast,
    LibraryItemPodcast,
)
from aioaudiobookshelf.schema.session import PlaybackSessionExpanded


class ItemsClient(BaseClient):
    """ItemsClient."""

    # delete all items (admin)

    async def get_library_item_book(
        self, *, book_id: str, expanded: bool = False
    ) -> LibraryItemBook | LibraryItemExpandedBook:
        """Get book library item.

        We only support expanded as parameter.
        """
        data = await self._get(f"/api/items/{book_id}?expanded={int(expanded)}")
        if not expanded:
            return LibraryItemBook.from_json(data)
        return LibraryItemExpandedBook.from_json(data)

    async def get_library_item_podcast(
        self, *, podcast_id: str, expanded: bool = False
    ) -> LibraryItemPodcast | LibraryItemExpandedPodcast:
        """Get book library item.

        We only support expanded as parameter.
        """
        data = await self._get(f"/api/items/{podcast_id}?expanded={int(expanded)}")
        if not expanded:
            return LibraryItemPodcast.from_json(data)
        return LibraryItemExpandedPodcast.from_json(data)

    # delete library item
    # update library item media
    # get item cover
    # upload cover
    # update cover
    # remove cover
    # match lib item

    async def get_playback_session(
        self,
        *,
        session_parameters: PlaybackSessionParameters,
        item_id: str,
        episode_id: str | None = None,
    ) -> PlaybackSessionExpanded:
        """Play a media item."""
        endpoint = f"/api/items/{item_id}/play"
        if episode_id is not None:
            endpoint += f"/{episode_id}"
        response = await self._post(endpoint, data=session_parameters.to_dict())
        return PlaybackSessionExpanded.from_json(response)

    # update audio track
    # scan item
    # get tone metadata
    # update chapters
    # tone scan

    async def _get_libray_item_batch(
        self, *, item_ids: list[str] | LibraryItemsBatchParameters
    ) -> bytes:
        if isinstance(item_ids, list):
            if not item_ids:
                return b""
            params = LibraryItemsBatchParameters(library_item_ids=item_ids)
        else:
            if not item_ids.library_item_ids:
                return b""
            params = item_ids

        return await self._post("/api/items/batch/get", data=params.to_dict())

    async def get_library_item_batch_book(
        self, *, item_ids: list[str] | LibraryItemsBatchParameters
    ) -> list[LibraryItemExpandedBook]:
        """Get multiple library items at once. Always expanded."""
        data = await self._get_libray_item_batch(item_ids=item_ids)
        if not data:
            return []
        return LibraryItemsBatchBookResponse.from_json(data).library_items

    async def get_library_item_batch_podcast(
        self, *, item_ids: list[str] | LibraryItemsBatchParameters
    ) -> list[LibraryItemExpandedPodcast]:
        """Get multiple library items at once. Always expanded."""
        data = await self._get_libray_item_batch(item_ids=item_ids)
        if not data:
            return []
        return LibraryItemsBatchPodcastResponse.from_json(data).library_items

    # batch delete, update, quick match
