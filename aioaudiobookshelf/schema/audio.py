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
    # null when the server could not probe the source file (e.g. unreadable media)
    duration: float | None
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
    # bit_rate / channels / channel_layout are derived from probing the media and
    # are null when the server could not probe the source file (e.g. unreadable media)
    duration: float | None
    bit_rate: Annotated[int | None, Alias("bitRate")] = None
    language: str | None = None
    codec: str
    time_base: Annotated[str, Alias("timeBase")]
    channels: int | None = None
    channel_layout: Annotated[str | None, Alias("channelLayout")] = None
    embedded_cover_art: Annotated[str | None, Alias("embeddedCoverArt")] = None
    mime_type: Annotated[str | None, Alias("mimeType")] = None
    # if part of a book
    # chapters: list[BookChapter]
    # id3 tags:
    # meta_tags: AudioMetaTags
