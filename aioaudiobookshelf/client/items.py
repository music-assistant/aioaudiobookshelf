"""Calls to /api/items."""

from aioaudiobookshelf.client._base import BaseClient
from aioaudiobookshelf.schema.calls_items import PlaybackSessionParameters
from aioaudiobookshelf.schema.library import (
    LibraryItemBook,
    LibraryItemExpandedBook,
    LibraryItemExpandedPodcast,
    LibraryItemPodcast,
)
from aioaudiobookshelf.schema.session import DeviceInfo, PlaybackSessionExpanded


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

    async def get_playback_session_music_assistant(
        self, *, device_info: DeviceInfo, book_id: str
    ) -> PlaybackSessionExpanded:
        """Music Assistant playback session for Audiobooks.

        Podcasts can be played directly, as they are single file.
        """
        params = PlaybackSessionParameters(
            device_info=device_info,
            force_direct_play=False,
            force_transcode=False,
            supported_mime_types=[],  # means no transcoding for us
        )
        endpoint = f"/api/items/{book_id}/play"
        response = await self._post(endpoint, data=params.to_dict())
        return PlaybackSessionExpanded.from_json(response)

    # update audio track
    # scan item
    # get tone metadata
    # update chapters
    # tone scan
    # batch delete, update, get, quick match
