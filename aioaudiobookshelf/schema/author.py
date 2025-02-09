"""Schema for Author."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel


@dataclass(kw_only=True)
class AuthorMinified(_BaseModel):
    """AuthorMinified.

    https://api.audiobookshelf.org/#author
    """

    id_: Annotated[str, Alias("id")]
    name: str


@dataclass(kw_only=True)
class Author(AuthorMinified):
    """Author."""

    asin: str | None = None
    description: str | None = None
    image_path: Annotated[str | None, Alias("imagePath")] = None
    added_at: Annotated[int, Alias("addedAt")]  # ms epoch
    updated_at: Annotated[int, Alias("updatedAt")]  # ms epoch


@dataclass(kw_only=True)
class AuthorExpanded(Author):
    """ABSAuthorExpanded."""

    num_books: Annotated[int, Alias("numBooks")]


@dataclass(kw_only=True)
class Narrator(_BaseModel):
    """Narrator."""

    id_: Annotated[str, Alias("id")]
    name: str
    num_books: Annotated[int, Alias("numBooks")]
