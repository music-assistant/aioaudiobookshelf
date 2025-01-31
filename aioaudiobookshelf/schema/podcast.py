"""Schema for podcasts."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .audio import AudioFile, AudioTrack


@dataclass
class PodcastMetadata(_BaseModel):
    """PodcastMetadata."""

    title: str | None
    author: str | None
    description: str | None
    release_date: Annotated[str | None, Alias("releaseDate")]
    genres: list[str]
    feed_url: Annotated[str | None, Alias("feedUrl")]
    image_url: Annotated[str | None, Alias("imageUrl")]
    itunes_page_url: Annotated[str | None, Alias("itunesPageUrl")]
    itunes_id: Annotated[int | None, Alias("itunesId")]
    # str: is not documented
    itunes_artist_id: Annotated[int | str | None, Alias("itunesArtistId")]
    explicit: bool
    language: str | None
    type_: Annotated[str | None, Alias("type")]


@dataclass
class PodcastMetadataMinified(PodcastMetadata):
    """PodcastMetadataMinified."""

    title_ignore_prefix: Annotated[str | None, Alias("titleIgnorePrefix")]


PodcastMetaDataExpanded = PodcastMetadataMinified


@dataclass
class PodcastEpisodeEnclosure(_BaseModel):
    """PodcastEpisodeEnclosure."""

    url: str
    type_: Annotated[str, Alias("type")]
    length: str


@dataclass
class _PodcastEpisodeBase(_BaseModel):
    """PodcastEpisode."""

    library_item_id: Annotated[str, Alias("libraryItemId")]
    id_: Annotated[str, Alias("id")]
    index: int | None
    season: str
    episode: str
    episode_type: Annotated[str, Alias("episodeType")]
    title: str
    subtitle: str
    description: str
    enclosure: PodcastEpisodeEnclosure
    pub_date: Annotated[str, Alias("pubDate")]
    published_at: Annotated[int, Alias("publishedAt")]  # ms posix epoch
    added_at: Annotated[int, Alias("addedAt")]  # ms posix epoch
    updated_at: Annotated[int, Alias("updatedAt")]  # ms posix epoch


@dataclass
class PodcastEpisode(_PodcastEpisodeBase):
    """PodcastEpisode."""

    # might be missing in playlists
    audio_file: AudioFile | None = None


@dataclass
class PodcastEpisodeExpanded(_PodcastEpisodeBase):
    """PodcastEpisodeExpanded."""

    audio_track: Annotated[AudioTrack, Alias("audioTrack")]
    duration: float
    size: int
    # might be missing in playlists
    audio_file: AudioFile | None = None


@dataclass
class _PodcastBase(_BaseModel):
    """_PodcastBase."""

    cover_path: Annotated[str | None, Alias("coverPath")]
    auto_download_episodes: Annotated[bool, Alias("autoDownloadEpisodes")]
    auto_download_schedule: Annotated[str, Alias("autoDownloadSchedule")]
    # None is not documented
    last_episode_check_ms: Annotated[int | None, Alias("lastEpisodeCheck")]
    max_episodes_to_keep: Annotated[int, Alias("maxEpisodesToKeep")]  # 0 = all
    max_new_episodes_to_download: Annotated[int, Alias("maxNewEpisodesToDownload")]


@dataclass
class Podcast(_PodcastBase):
    """ABSPodcast."""

    library_item_id: Annotated[str, Alias("libraryItemId")]
    metadata: PodcastMetadata
    tags: list[str]
    episodes: list[PodcastEpisode]


@dataclass
class PodcastMinified(_PodcastBase):
    """ABSPodcastMinified."""

    metadata: PodcastMetadataMinified
    size: int  # bytes
    num_episodes: Annotated[int, Alias("numEpisodes")]


@dataclass
class PodcastExpanded(_PodcastBase):
    """PodcastEpisodeExpanded."""

    library_item_id: Annotated[str, Alias("libraryItemId")]
    tags: list[str]
    size: int  # bytes
    metadata: PodcastMetaDataExpanded
    episodes: list[PodcastEpisodeExpanded]
