"""Calls to /api/me."""

from collections.abc import AsyncGenerator
from typing import Any

from aioaudiobookshelf.client._base import BaseClient
from aioaudiobookshelf.exceptions import NotFoundError
from aioaudiobookshelf.schema.calls_me import (
    ItemsInProgressResponse,
    MeListeningSessionsParameters,
    MeListeningSessionsResponse,
)
from aioaudiobookshelf.schema.media_progress import MediaProgress
from aioaudiobookshelf.schema.shelf import ShelfLibraryItemMinified
from aioaudiobookshelf.schema.user import User


class MeClient(BaseClient):
    """MeClient."""

    async def get_my_user(self) -> User:
        """Get this client's user."""
        data = await self._get("/api/me")
        return User.from_json(data)

    async def get_my_listening_sessions(self) -> AsyncGenerator[MeListeningSessionsResponse]:
        """Get this user's listening sessions."""
        page_cnt = 0
        params = MeListeningSessionsParameters(
            items_per_page=self.session_config.pagination_items_per_page, page=page_cnt
        )
        while True:
            params.page = page_cnt
            response = await self._get("/api/me/listening-sessions", params.to_dict())
            page_cnt += 1
            page = MeListeningSessionsResponse.from_json(response)
            yield page
            # guard a page size of 0, which would never reach the total
            if page.items_per_page <= 0 or page_cnt * page.items_per_page >= page.total:
                return

    async def get_my_items_in_progress(self, *, limit: int = 25) -> list[ShelfLibraryItemMinified]:
        """Get this user's unfinished items, the most recently listened to first.

        Abs counts an item as in progress once it has a position, see its MeController.js.
        """
        response = await self._get("/api/me/items-in-progress", params={"limit": limit})
        return ItemsInProgressResponse.from_json(response).library_items

    # listening stats
    # remove item from continue listening

    async def get_my_media_progress(
        self, *, item_id: str, episode_id: str | None = None
    ) -> MediaProgress | None:
        """Get a MediaProgress, returns None if none found."""
        endpoint = f"/api/me/progress/{item_id}"
        if episode_id is not None:
            endpoint += f"/{episode_id}"
        try:
            response = await self._get(endpoint=endpoint)
        except NotFoundError:
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
        mark_as_finished_time_remaining: int | None = None,
        mark_as_finished_percent_complete: int | None = None,
    ) -> None:
        """Update progress of media item.

        The mark_as_finished_* are a library's settings. Abs only applies them to
        /api/me/progress if the caller sends them, unlike a session sync, where it
        adds them itself. Without them abs falls back to 10s remaining.

        Three calls, because abs cannot take this in one (models/MediaProgress.js):
            - with isFinished in the payload, progress in the same payload is ignored
            - unsetting isFinished drops currentTime from the payload and zeroes it
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
        if duration_seconds <= 0:
            # abs has no duration for e.g. a podcast episode it did not probe, so there is
            # no percentage to send, and a duration of 0 would overwrite what abs knows
            await self._patch(endpoint, data={"currentTime": progress_seconds})
            self.logger.debug(
                "Updated position of %s, id %s, its duration is unknown.", logger_item, item_id
            )
            return
        percentage = progress_seconds / duration_seconds
        await self._patch(
            endpoint,
            data={"progress": percentage},
        )
        data: dict[str, Any] = {"duration": duration_seconds, "currentTime": progress_seconds}
        if mark_as_finished_time_remaining is not None:
            data["markAsFinishedTimeRemaining"] = mark_as_finished_time_remaining
        if mark_as_finished_percent_complete is not None:
            data["markAsFinishedPercentComplete"] = mark_as_finished_percent_complete
        await self._patch(endpoint, data=data)
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
