"""Schema for audio."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .file import FileMetadata


@dataclass
class AudioBookmark(_BaseModel):
    """AudioBookmark. No variants.

    https://api.audiobookshelf.org/#audio-bookmark
    """

    library_item_id: Annotated[str, Alias("libraryItemId")]
    title: str
    time: int  # seconds
    created_at: Annotated[int, Alias("createdAt")]  # unix epoch ms


@dataclass
class AudioTrack(_BaseModel):
    """ABS audioTrack. No variants.

    https://api.audiobookshelf.org/#audio-track
    """

    index: int | None
    start_offset: Annotated[float, Alias("startOffset")]
    duration: float
    title: str
    content_url: Annotated[str, Alias("contentUrl")]
    mime_type: str
    metadata: FileMetadata | None
