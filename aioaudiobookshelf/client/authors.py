"""Calls to /api/authors."""

from aioaudiobookshelf.client._base import BaseClient
from aioaudiobookshelf.schema.author import Author
from aioaudiobookshelf.schema.calls_authors import AuthorWithItems, AuthorWithItemsAndSeries


class AuthorsClient(BaseClient):
    """AuthorsClient."""

    async def get_author(
        self, *, author_id: str, include_items: bool = False, include_series: bool = False
    ) -> Author | AuthorWithItems | AuthorWithItemsAndSeries:
        """Get an author.

        Include series always includes items.
        """
        response_cls: type[Author | AuthorWithItems | AuthorWithItemsAndSeries] = Author
        if include_series:
            include_items = True
        endpoint = f"/api/authors/{author_id}"
        if include_items:
            endpoint += "?include=items"
            response_cls = AuthorWithItems
        if include_series:
            endpoint += ",series"
            response_cls = AuthorWithItemsAndSeries

        response = await self._get(endpoint)
        return response_cls.from_json(response)

    # update author
    # match author
    # get author image
