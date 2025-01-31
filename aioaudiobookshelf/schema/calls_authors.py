"""Calls to /api/authors."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .author import Author
from .library import LibraryItemMinified


@dataclass
class AuthorSeries(_BaseModel):
    """AuthorSeries."""

    id_: Annotated[str, Alias("id")]
    name: str
    items: list[LibraryItemMinified]


@dataclass
class AuthorWithItems(Author):
    """AuthorWithItems."""

    library_items: Annotated[list[LibraryItemMinified], Alias("libraryItems")]


@dataclass
class AuthorWithItemsAndSeries(AuthorWithItems):
    """AuthorWithItemsAndSeries."""

    series: list[AuthorSeries]
