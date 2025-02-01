"""Schema for media progress."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .book import BookExpanded
from .podcast import PodcastEpisode, PodcastExpanded


@dataclass(kw_only=True)
class MediaProgress(_BaseModel):
    """MediaProgress."""

    id_: Annotated[str, Alias("id")]
    library_item_id: Annotated[str, Alias("libraryItemId")]
    episode_id: Annotated[str | None, Alias("episodeId")] = None
    duration: float  # seconds
    progress: float  # percent 0->1
    current_time: Annotated[float, Alias("currentTime")]  # seconds
    is_finished: Annotated[bool, Alias("isFinished")]
    hide_from_continue_listening: Annotated[bool, Alias("hideFromContinueListening")]
    last_update: Annotated[int, Alias("lastUpdate")]  # ms epoch
    started_at: Annotated[int, Alias("startedAt")]  # ms epoch
    finished_at: Annotated[int | None, Alias("finishedAt")] = None  # ms epoch


@dataclass(kw_only=True)
class MediaProgressWithMediaBook(MediaProgress):
    """MediaProgressWithMediaBook."""

    media: BookExpanded


@dataclass(kw_only=True)
class MediaProgressWithMediaPodcast(MediaProgress):
    """MediaProgressWithMediaPodcast."""

    media: PodcastExpanded
    episode: PodcastEpisode
