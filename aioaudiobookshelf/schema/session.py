"""Schema for playback session."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .audio import AudioTrack
from .book import BookChapter, BookMetadata
from .podcast import PodcastMetadata


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
    library_id: Annotated[str, Alias("libraryId")]
    library_item_id: Annotated[str, Alias("libraryItemId")]
    episode_id: Annotated[str | None, Alias("episodeId")] = None
    media_type: Annotated[str, Alias("mediaType")]
    media_metadata: Annotated[PodcastMetadata | BookMetadata, Alias("mediaMetadata")]
    display_title: Annotated[str, Alias("displayTitle")]
    display_author: Annotated[str, Alias("displayAuthor")]
    cover_path: Annotated[str, Alias("coverPath")]
    duration: float
    # 0: direct play, 1: direct stream, 2: transcode, 3: local
    play_method: Annotated[PlaybackMethod, Alias("playMethod")]
    media_player: Annotated[str, Alias("mediaPlayer")]
    device_info: Annotated[DeviceInfo, Alias("deviceInfo")]
    server_version: Annotated[str, Alias("serverVersion")]
    # YYYY-MM-DD
    date: str
    day_of_week: Annotated[str, Alias("dayOfWeek")]
    time_listening: Annotated[float, Alias("timeListening")]  # s
    start_time: Annotated[float, Alias("startTime")]  # s
    current_time: Annotated[float, Alias("currentTime")]  # s
    started_at: Annotated[int, Alias("startedAt")]  # ms since Unix Epoch
    updated_at: Annotated[int, Alias("updatedAt")]  # ms since Unix Epoch
    chapters: list[BookChapter] = field(default_factory=list)


@dataclass(kw_only=True)
class PlaybackSessionExpanded(PlaybackSession):
    """PlaybackSessionExpanded."""

    audio_tracks: Annotated[list[AudioTrack], Alias("audioTracks")]
    # videoTrack
    # libraryItem
