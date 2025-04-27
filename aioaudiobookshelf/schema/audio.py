"""Schema for audio."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .file import FileMetadata


@dataclass(kw_only=True)
class AudioBookmark(_BaseModel):
    """AudioBookmark. No variants.

    https://api.audiobookshelf.org/#audio-bookmark
    """

    library_item_id: Annotated[str, Alias("libraryItemId")]
    title: str
    time: int  # seconds
    created_at: Annotated[int, Alias("createdAt")]  # unix epoch ms


@dataclass(kw_only=True)
class AudioTrack(_BaseModel):
    """ABS audioTrack. No variants.

    https://api.audiobookshelf.org/#audio-track
    """

    index: int | None
    start_offset: Annotated[float, Alias("startOffset")]
    duration: float
    title: str
    content_url: Annotated[str, Alias("contentUrl")]
    metadata: FileMetadata | None
    # is missing if part of library...
    mime_type: str | None = None


@dataclass(kw_only=True)
class AudioFile(_BaseModel):
    """Audiofile."""

    index: int
    ino: str
    metadata: FileMetadata
    added_at: Annotated[int, Alias("addedAt")]
    updated_at: Annotated[int, Alias("updatedAt")]
    track_num_from_meta: Annotated[int | None, Alias("trackNumFromMeta")] = None
    disc_num_from_meta: Annotated[int | None, Alias("discNumFromMeta")] = None
    track_num_from_filename: Annotated[int | None, Alias("trackNumFromFilename")] = None
    disc_num_from_filename: Annotated[int | None, Alias("discNumFromFilename")] = None
    manually_verified: Annotated[bool, Alias("manuallyVerified")]
    exclude: bool
    error: str | None = None
    format: str
    duration: float | None
    bit_rate: Annotated[int, Alias("bitRate")]
    language: str | None = None
    codec: str
    time_base: Annotated[str, Alias("timeBase")]
    channels: int
    channel_layout: Annotated[str, Alias("channelLayout")]
    embedded_cover_art: Annotated[str | None, Alias("embeddedCoverArt")] = None
    mime_type: Annotated[str, Alias("mimeType")]
    # if part of a book
    # chapters: list[BookChapter]
    # id3 tags:
    # meta_tags: AudioMetaTags
