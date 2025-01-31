"""Calls to /api/series."""

from aioaudiobookshelf.client._base import BaseClient
from aioaudiobookshelf.schema.calls_series import SeriesWithProgress
from aioaudiobookshelf.schema.series import Series


class SeriesClient(BaseClient):
    """SeriesClient."""

    async def get_series(
        self, *, series_id: str, include_progress: bool = False
    ) -> Series | SeriesWithProgress:
        """Get an author.

        Include series always includes items.
        """
        response_cls: type[Series | SeriesWithProgress] = Series
        endpoint = f"/api/series/{series_id}"
        if include_progress:
            endpoint += "?include=progress"
            response_cls = SeriesWithProgress

        response = await self._get(endpoint)
        return response_cls.from_json(response)

    # update series
