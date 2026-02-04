"""Schema for streams."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from aioaudiobookshelf.schema import _BaseModel
from aioaudiobookshelf.schema.library import LibraryItemExpanded
from aioaudiobookshelf.schema.podcast import PodcastEpisodeExpanded


@dataclass(kw_only=True)
class Stream(_BaseModel):
    """Stream."""

    id_: Annotated[str, Alias("id")]
    user_id: Annotated[str, Alias("userId")]

    library_item: Annotated[LibraryItemExpanded, Alias("libraryItem")]
    episode: PodcastEpisodeExpanded | None = None
    segment_length: Annotated[int, Alias("segmentLength")]
    playlist_path: Annotated[str, Alias("playlistPath")]
    client_playlist_uri: Annotated[str, Alias("clientPlaylistUri")]
    start_time: Annotated[float, Alias("startTime")]
    segment_start_number: Annotated[int, Alias("segmentStartNumber")]
    is_transcode_complete: Annotated[bool, Alias("isTranscodeComplete")]


@dataclass(kw_only=True)
class StreamProgress(_BaseModel):
    """StreamProgress."""

    stream: str
    percent: str
    chunks: list[str]
    num_segments: Annotated[int, Alias("numSegments")]
