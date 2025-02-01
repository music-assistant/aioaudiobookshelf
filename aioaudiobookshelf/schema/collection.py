"""Schema for Collections."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .library import LibraryItemBook, LibraryItemExpandedBook


@dataclass(kw_only=True)
class _CollectionBase(_BaseModel):
    """_CollectionBase."""

    id_: Annotated[str, Alias("id")]
    library_id: Annotated[str, Alias("libraryId")]
    user_id: Annotated[str | None, Alias("userId")] = None
    name: str
    description: str | None = None
    last_update: Annotated[int, Alias("lastUpdate")]  # ms epoch
    created_at: Annotated[int, Alias("createdAt")]  # ms epoch


@dataclass(kw_only=True)
class Collection(_CollectionBase):
    """Collection."""

    books: list[LibraryItemBook]


@dataclass(kw_only=True)
class CollectionExpanded(_CollectionBase):
    """Collection."""

    books: list[LibraryItemExpandedBook]
