"""Params and responses for collections."""

from dataclasses import dataclass

from aioaudiobookshelf.schema.collection import CollectionExpanded

from . import _BaseModel


@dataclass(kw_only=True)
class AllCollectionsResponse(_BaseModel):
    """AllCollectionsResponse."""

    collections: list[CollectionExpanded]
