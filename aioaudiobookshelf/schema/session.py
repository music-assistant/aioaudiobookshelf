"""Schema for playback session."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Annotated, Any

from mashumaro.types import Alias

from . import _BaseModel
from .audio import AudioTrack
from .book import BookChapter, BookMetadata
from .podcast import PodcastEpisodeChapter, PodcastMetadata


@dataclass(kw_only=True)
class DeviceInfo(_BaseModel):
    """DeviceInfo. No variants.

    https://api.audiobookshelf.org/#device-info-parameters
    https://api.audiobookshelf.org/#device-info
    https://github.com/advplyr/audiobookshelf/blob/master/server/objects/DeviceInfo.js#L3
    """

    device_id: Annotated[str, Alias("deviceId")] = ""
    client_name: Annotated[str, Alias("clientName")] = ""
    client_version: Annotated[str, Alias("clientVersion")] = ""
    manufacturer: str = ""
    model: str = ""
    # sdkVersion # meant for an Android client


class PlaybackMethod(Enum):
    """Playback method in playback session."""

    DIRECT_PLAY = 0
    DIRECT_STREAM = 1
    TRANSCODE = 2
    LOCAL = 3


@dataclass(kw_only=True)
class PlaybackSession(_BaseModel):
    """PlaybackSession."""

    id_: Annotated[str, Alias("id")]
    user_id: Annotated[str, Alias("userId")]
    # null in a stored session abs could not map, e.g. a migrated one,
    # see its objects/PlaybackSession.js
    library_id: Annotated[str | None, Alias("libraryId")]
    library_item_id: Annotated[str | None, Alias("libraryItemId")]
    episode_id: Annotated[str | None, Alias("episodeId")] = None
    media_type: Annotated[str, Alias("mediaType")]
    # BookMetadata first: it needs authors, narrators and series, which a podcast
    # does not send, while PodcastMetadata would happily swallow a book.
    # Stored sessions may have none, e.g. local ones or those migrated from abs v1.
    media_metadata: Annotated[BookMetadata | PodcastMetadata | None, Alias("mediaMetadata")]
    display_title: Annotated[str, Alias("displayTitle")]
    display_author: Annotated[str | None, Alias("displayAuthor")] = None
    cover_path: Annotated[str | None, Alias("coverPath")] = None
    duration: float | None
    # 0: direct play, 1: direct stream, 2: transcode, 3: local
    play_method: Annotated[PlaybackMethod, Alias("playMethod")]
    media_player: Annotated[str | None, Alias("mediaPlayer")]
    device_info: Annotated[DeviceInfo, Alias("deviceInfo")]
    server_version: Annotated[str | None, Alias("serverVersion")]
    # YYYY-MM-DD
    date: str
    day_of_week: Annotated[str, Alias("dayOfWeek")]
    # abs reads a stored 0 back as null, see its objects/PlaybackSession.js
    time_listening: Annotated[float | None, Alias("timeListening")]  # s
    start_time: Annotated[float, Alias("startTime")]  # s
    current_time: Annotated[float, Alias("currentTime")]  # s
    started_at: Annotated[int, Alias("startedAt")]  # ms since Unix Epoch
    updated_at: Annotated[int, Alias("updatedAt")]  # ms since Unix Epoch
    # an episode's chapters as stored, see PodcastEpisodeChapter
    chapters: list[BookChapter | PodcastEpisodeChapter] = field(default_factory=list)


@dataclass(kw_only=True)
class PlaybackSessionExpanded(PlaybackSession):
    """PlaybackSessionExpanded."""

    # abs sets these when it opens a session, only stored ones may lack them
    library_id: Annotated[str, Alias("libraryId")]
    library_item_id: Annotated[str, Alias("libraryItemId")]
    media_metadata: Annotated[BookMetadata | PodcastMetadata, Alias("mediaMetadata")]
    duration: float
    media_player: Annotated[str, Alias("mediaPlayer")]
    server_version: Annotated[str, Alias("serverVersion")]
    time_listening: Annotated[float, Alias("timeListening")]  # s
    audio_tracks: Annotated[list[AudioTrack], Alias("audioTracks")]
    # videoTrack
    # libraryItem

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        """Read a null duration as 0, as abs 2.7.1 and newer sends it for an unprobed episode."""
        if d.get("duration") is None:
            return {**d, "duration": 0.0}
        return d
