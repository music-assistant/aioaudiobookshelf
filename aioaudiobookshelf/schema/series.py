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
class SeriesBooks(_SeriesBase):
    """SeriesBooks."""

    added_at: Annotated[int, Alias("addedAt")]  # ms epoch
    name_ignore_prefix: Annotated[str, Alias("nameIgnorePrefix")]
    name_ignore_prefix_sort: Annotated[str, Alias("nameIgnorePrefixSort")]
    type_: Annotated[str, Alias("type")]
    # books: list[LibraryItemBookSeries]
    total_duration: Annotated[float, Alias("totalDuration")]  # s


@dataclass
class SeriesSequence(_SeriesBase):
    """Series Sequence."""

    sequence: str | None
