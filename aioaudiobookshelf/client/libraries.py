"""Calls to /api/libraries."""

from collections.abc import AsyncGenerator
from typing import TypeVar

from mashumaro.mixins.json import DataClassJSONMixin

from aioaudiobookshelf.client._base import BaseClient
from aioaudiobookshelf.schema.calls_library import (
    AllLibrariesResponse,
    LibraryCollectionsMinifiedResponse,
    LibraryCollectionsResponse,
    LibraryItemsMinifiedResponse,
    LibraryItemsResponse,
    LibraryPlaylistsResponse,
    LibrarySeriesMinifiedResponse,
    LibrarySeriesResponse,
    LibraryWithFilterDataResponse,
)
from aioaudiobookshelf.schema.library import Library

ResponseMinified = TypeVar("ResponseMinified", bound=DataClassJSONMixin)
ResponseNormal = TypeVar("ResponseNormal", bound=DataClassJSONMixin)


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

    async def _get_library_with_pagination(
        self,
        *,
        endpoint: str,
        minified: bool = False,
        response_cls_minified: type[ResponseMinified],
        response_cls: type[ResponseNormal],
    ) -> AsyncGenerator[ResponseMinified | ResponseNormal]:
        page_cnt = 0
        params: dict[str, int | str] = {
            "minified": int(minified),
            "limit": self.session_config.pagination_items_per_page,
        }
        while True:
            params["page"] = page_cnt
            response = await self._get(endpoint, params)
            page_cnt += 1
            if minified:
                yield response_cls_minified.from_json(response)
            else:
                yield response_cls.from_json(response)

    async def get_library_items(
        self, *, library_id: str
    ) -> AsyncGenerator[LibraryItemsResponse | LibraryItemsMinifiedResponse]:
        """Get library items.

        Returns only minified items at this point.
        """
        # only minified response is supported at API
        minified: bool = True
        endpoint = f"/api/libraries/{library_id}/items"
        async for result in self._get_library_with_pagination(
            endpoint=endpoint,
            minified=minified,
            response_cls_minified=LibraryItemsMinifiedResponse,
            response_cls=LibraryItemsResponse,
        ):
            yield result

    # remove item with issues
    # get lib podcast episode downloads

    async def get_library_series(
        self, *, library_id: str
    ) -> AsyncGenerator[LibrarySeriesMinifiedResponse | LibrarySeriesResponse]:
        """Get series in that library.

        Returns only minified items at this point.
        """
        # only minified response is supported
        minified: bool = True
        endpoint = f"/api/libraries/{library_id}/series"
        async for result in self._get_library_with_pagination(
            endpoint=endpoint,
            minified=minified,
            response_cls=LibrarySeriesResponse,
            response_cls_minified=LibrarySeriesMinifiedResponse,
        ):
            yield result

    async def get_library_collections(
        self, *, library_id: str
    ) -> AsyncGenerator[LibraryCollectionsMinifiedResponse | LibraryCollectionsResponse]:
        """Get collections in that library.

        Returns only minified items at this point.
        """
        # only minified response is supported
        minified: bool = True
        endpoint = f"/api/libraries/{library_id}/collections"
        async for result in self._get_library_with_pagination(
            endpoint=endpoint,
            minified=minified,
            response_cls=LibraryCollectionsResponse,
            response_cls_minified=LibraryCollectionsMinifiedResponse,
        ):
            yield result

    async def get_library_playlists(
        self, *, library_id: str
    ) -> AsyncGenerator[LibraryPlaylistsResponse]:
        """Get collections in that library.

        Returns only minified items at this point.
        """
        endpoint = f"/api/libraries/{library_id}/playlists"
        async for result in self._get_library_with_pagination(
            endpoint=endpoint,
            minified=False,  # there is no minified version
            response_cls=LibraryPlaylistsResponse,
            response_cls_minified=LibraryPlaylistsResponse,
        ):
            yield result
