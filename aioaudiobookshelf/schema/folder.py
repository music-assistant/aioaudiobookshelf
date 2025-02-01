"""Folder Schema."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel


@dataclass(kw_only=True)
class Folder(_BaseModel):
    """Folder."""

    id_: Annotated[str, Alias("id")]
    full_path: Annotated[str, Alias("fullPath")]
    library_id: Annotated[str, Alias("libraryId")]
    added_at: Annotated[int, Alias("addedAt")]  # ms epoch
