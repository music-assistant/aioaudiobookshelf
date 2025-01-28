"""Schema for Author."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel


@dataclass
class AuthorMinified(_BaseModel):
    """AuthorMinified.

    https://api.audiobookshelf.org/#author
    """

    id_: Annotated[str, Alias("id")]
    name: str


@dataclass
class Author(AuthorMinified):
    """Author."""

    asin: str | None
    description: str | None
    image_path: Annotated[str | None, Alias("imagePath")]
    added_at: Annotated[int, Alias("addedAt")]  # ms epoch
    updated_at: Annotated[int, Alias("updatedAt")]  # ms epoch


@dataclass
class AuthorExpanded(Author):
    """ABSAuthorExpanded."""

    num_books: Annotated[int, Alias("numBooks")]
