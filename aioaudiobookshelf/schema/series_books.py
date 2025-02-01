"""SeriesBase classes."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from .library import LibraryItemBook, LibraryItemMinifiedBook
from .series import _SeriesBase


@dataclass(kw_only=True)
class _SeriesBooksBase(_SeriesBase):
    """SeriesBooks."""

    added_at: Annotated[int, Alias("addedAt")]  # ms epoch
    name_ignore_prefix: Annotated[str, Alias("nameIgnorePrefix")]
    name_ignore_prefix_sort: Annotated[str, Alias("nameIgnorePrefixSort")]
    type_: Annotated[str, Alias("type")]
    total_duration: Annotated[float, Alias("totalDuration")]  # s


@dataclass(kw_only=True)
class SeriesBooks(_SeriesBooksBase):
    """SeriesBooks."""

    books: list[LibraryItemBook]


@dataclass(kw_only=True)
class SeriesBooksMinified(_SeriesBase):
    """SeriesBooks."""

    books: list[LibraryItemMinifiedBook]
