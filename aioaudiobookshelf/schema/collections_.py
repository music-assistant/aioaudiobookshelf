"""Schema for Collections."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .library import LibraryItemBook, LibraryItemExpandedBook


@dataclass
class _CollectionBase(_BaseModel):
    """_CollectionBase."""

    id_: Annotated[str, Alias("id")]
    library_id: Annotated[str, Alias("libraryId")]
    # user_id: Annotated[str, Alias("userId")]
    name: str
    description: str | None
    last_update: Annotated[int, Alias("lastUpdate")]  # ms epoch
    created_at: Annotated[int, Alias("createdAt")]  # ms epoch


@dataclass
class Collection(_CollectionBase):
    """Collection."""

    books: list[LibraryItemBook]


@dataclass
class CollectionExpanded(_CollectionBase):
    """Collection."""

    books: list[LibraryItemExpandedBook]
