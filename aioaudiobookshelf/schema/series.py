"""Schema for series."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel


@dataclass
class _SeriesBase(_BaseModel):
    """_SeriesBase."""

    id_: Annotated[str, Alias("id")]
    name: str


# in get_library call including filterdata we get only id and name of series
SeriesFilterData = _SeriesBase


@dataclass
class Series(_SeriesBase):
    """Series."""

    description: str | None
    added_at: Annotated[int, Alias("addedAt")]  # ms epoch
    updated_at: Annotated[int, Alias("updatedAt")]  # ms epoch


@dataclass
class SeriesNumBooks(_SeriesBase):
    """SeriesNumBooks."""

    name_ignore_prefix: Annotated[str, Alias("nameIgnorePrefix")]
    library_item_ids: Annotated[list[str], Alias("libraryItemIds")]
    num_books: Annotated[int, Alias("numBooks")]


@dataclass
class SeriesSequence(_SeriesBase):
    """Series Sequence."""

    sequence: str | None
