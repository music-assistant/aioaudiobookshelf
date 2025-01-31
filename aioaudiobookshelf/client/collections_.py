"""Calls to /api/collections."""

from aioaudiobookshelf.schema.calls_collections import AllCollectionsResponse
from aioaudiobookshelf.schema.collection import CollectionExpanded

from ._base import BaseClient


class CollectionsClient(BaseClient):
    """CollectionsClient."""

    # create collection

    async def get_all_collections(self) -> list[CollectionExpanded]:
        """Get all collections accessible to user."""
        data = await self._get(endpoint="/api/collections")
        return AllCollectionsResponse.from_json(data).collections

    async def get_collection(self, *, collection_id: str) -> CollectionExpanded:
        """Get a collection."""
        data = await self._get(endpoint=f"/api/collections/{collection_id}")
        return CollectionExpanded.from_json(data)

    # update
    # delete
    # add book
    # remove book
    # batch add + remove
