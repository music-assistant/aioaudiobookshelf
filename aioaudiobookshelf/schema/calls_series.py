"""Calls to /api/series."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .series import Series


@dataclass
class SeriesProgress(_BaseModel):
    """SeriesProgress."""

    library_item_ids: Annotated[list[str], Alias("libraryItemIds")]
    library_items_ids_finished: Annotated[list[str], Alias("libraryItemIdsFinished")]
    is_finished: Annotated[bool, Alias("isFinished")]


@dataclass
class SeriesWithProgress(Series):
    """SeriesWithProgress."""

    progress: SeriesProgress
