"""Calls to /api/me."""

from collections.abc import AsyncGenerator

from aioaudiobookshelf.client._base import BaseClient
from aioaudiobookshelf.schema.calls_me import (
    MeListeningSessionsParameters,
    MeListeningSessionsResponse,
)
from aioaudiobookshelf.schema.media_progress import MediaProgress
from aioaudiobookshelf.schema.user import User


class MeClient(BaseClient):
    """MeClient."""

    async def get_my_user(self) -> User:
        """Get this client's user."""
        data = await self._get("/api/me")
        return User.from_json(data)

    async def get_my_listening_sessions(self) -> AsyncGenerator[MeListeningSessionsResponse]:
        """Get this user's listening sessions."""
        raise NotImplementedError("PodcastMetadata not fully returned.")
        page_cnt = 0
        params = MeListeningSessionsParameters(
            items_per_page=self.session_config.pagination_items_per_page, page=page_cnt
        )
        while True:
            params.page = page_cnt
            response = await self._get("/api/me/listening-sessions", params.to_dict())
            page_cnt += 1
            yield MeListeningSessionsResponse.from_json(response)

    # listening stats
    # remove item from continue listening

    async def get_my_media_progress(
        self, *, item_id: str, episode_id: str | None = None
    ) -> MediaProgress | None:
        """Get a MediaProgress, returns None if none found."""
        endpoint = f"/api/me/progress/{item_id}"
        if episode_id is not None:
            endpoint += f"/{episode_id}"
        response = await self._get(endpoint=endpoint)
        if not response:
            return None
        return MediaProgress.from_json(response)

    # batch create/ update media progress

    async def update_my_media_progress(
        self,
        *,
        item_id: str,
        episode_id: str | None = None,
        duration_seconds: float,
        progress_seconds: float,
        is_finished: bool,
    ) -> None:
        """Update progress of media item.

        0 <= progress_percent <= 1

        Notes:
            - progress in abs is percentage
            - multiple parameters in one call don't work in all combinations
            - currentTime is current position in s
            - currentTime works only if duration is sent as well, but then don't
              send progress at the same time.
        """
        logger_item = "audiobook" if not episode_id else "podcast"
        endpoint = f"/api/me/progress/{item_id}"
        if episode_id is not None:
            endpoint += f"/{episode_id}"
        await self._patch(
            endpoint,
            data={"isFinished": is_finished},
        )
        if is_finished:
            self.logger.debug("Marked %s, id %s finished.", logger_item, item_id)
            return
        percentage = progress_seconds / duration_seconds
        await self._patch(
            endpoint,
            data={"progress": percentage},
        )
        await self._patch(
            endpoint,
            data={"duration": duration_seconds, "currentTime": progress_seconds},
        )
        self.logger.debug(
            "Updated progress of %s, id %s to %.2f%%.", logger_item, item_id, percentage * 100
        )

    async def remove_my_media_progress(self, *, media_progress_id: str) -> None:
        """Remove a single media progress."""
        await self._delete(f"/api/me/progress/{media_progress_id}")

    # create, update, remove bookmark
    # change password
    # get lib items in progress
    # remove series from continue listening
