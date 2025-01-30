"""Calls to /api/libraries."""

from collections.abc import AsyncGenerator

from aioaudiobookshelf.client._base import BaseClient
from aioaudiobookshelf.schema.calls_library import (
    AllLibrariesResponse,
    LibraryItemsMinifiedResponse,
    LibraryItemsResponse,
    LibraryWithFilterDataResponse,
)
from aioaudiobookshelf.schema.library import Library


class LibrariesClient(BaseClient):
    """LibrariesClient."""

    # create library

    async def get_all_libraries(self) -> list[Library]:
        """Get all user accessible libraries."""
        response = await self._get("/api/libraries")
        return AllLibrariesResponse.from_json(response).libraries

    async def get_library(self, *, library_id: str) -> Library:
        """Get single library."""
        response = await self._get(f"/api/libraries/{library_id}")
        return Library.from_json(response)

    async def get_library_with_filterdata(
        self, *, library_id: str
    ) -> LibraryWithFilterDataResponse:
        """Get single library including filterdata."""
        response = await self._get(f"/api/libraries/{library_id}?include=filterdata")
        return LibraryWithFilterDataResponse.from_json(response)

    # update library
    # delete library

    async def get_library_items(
        self,
        *,
        library_id: str,
        minified: bool = True,
    ) -> AsyncGenerator[LibraryItemsResponse | LibraryItemsMinifiedResponse]:
        """Get library items.

        There are a couple of options to this API call. Currently, collapseseries is set to False,
        and other parameters than minified are not supported. Pagination is applied according to
        SessionConfiguration of client.
        """
        page_cnt = 0
        params: dict[str, int | str] = {
            "minified": int(minified),
            "limit": self.session_config.pagination_items_per_page,
            "collapseseries": 0,
        }
        while True:
            params["page"] = page_cnt
            endpoint = f"/api/libraries/{library_id}/items"
            response = await self._get(endpoint, params)
            page_cnt += 1
            if minified:
                yield LibraryItemsMinifiedResponse.from_json(response)
            else:
                yield LibraryItemsResponse.from_json(response)

    # remove item with issues
