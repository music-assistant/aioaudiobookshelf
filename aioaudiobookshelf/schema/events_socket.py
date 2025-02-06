"""Scheme for socket client."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .media_progress import MediaProgress


@dataclass(kw_only=True)
class UserItemProgressUpdatedEvent(_BaseModel):
    """UserItemProgressUpdatedEvent."""

    id_: Annotated[str, Alias("id")]
    data: MediaProgress


@dataclass(kw_only=True)
class PodcastEpisodeDownload(_BaseModel):
    """PodcastEpisodeDownload."""

    id_: Annotated[str, Alias("id")]
    episode_display_title: Annotated[str, Alias("episodeDisplayTitle")]
    url: str
    library_item_id: Annotated[str, Alias("libraryItemId")]
    library_id: Annotated[str, Alias("libraryId")]
    is_finished: Annotated[bool, Alias("isFinished")]
    failed: bool
    started_at: Annotated[int | None, Alias("startedAt")] = None
    created_at: Annotated[int, Alias("createdAt")]
    finished_at: Annotated[int | None, Alias("finishedAt")] = None
    podcast_title: Annotated[str | None, Alias("podcastTitle")] = None
    podcast_explicit: Annotated[bool, Alias("podcastExplicit")]
    season: str | None = None
    episode: str | None = None
    episode_type: Annotated[str, Alias("episodeType")]
    published_at: Annotated[int | None, Alias("publishedAt")] = None


@dataclass(kw_only=True)
class LibraryItemRemoved(_BaseModel):
    """LibraryItemRemoved."""

    id_: Annotated[str, Alias("id")]
