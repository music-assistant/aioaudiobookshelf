"""Schema for playlist."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias, Discriminator

from aioaudiobookshelf.schema.podcast import PodcastEpisodeExpanded

from . import _BaseModel
from .library import LibraryItemExpandedBook, LibraryItemMinifiedPodcast


@dataclass(kw_only=True)
class PlaylistItem(_BaseModel):
    """PlaylistItem."""

    library_item_id: Annotated[str, Alias("libraryItemId")]
    episode_id: Annotated[str | None, Alias("episodeId")] = None


@dataclass(kw_only=True)
class PlaylistItemExpanded(_BaseModel):
    """PlaylistExpanded."""

    class Config(PlaylistItem.Config):
        """Config."""

        # can't use field as episode_id is either existing or not.
        discriminator = Discriminator(
            include_subtypes=True,
        )


@dataclass(kw_only=True)
class PlaylistItemExpandedBook(PlaylistItemExpanded):
    """PlaylistExpanded."""

    library_item: Annotated[LibraryItemExpandedBook, Alias("libraryItem")]


@dataclass(kw_only=True)
class PlaylistItemExpandedPodcast(PlaylistItemExpanded):
    """PlaylistItemExpandedPodcast."""

    library_item: Annotated[LibraryItemMinifiedPodcast, Alias("libraryItem")]
    episode_id: Annotated[str, Alias("episodeId")]
    episode: PodcastEpisodeExpanded


@dataclass(kw_only=True)
class _PlaylistBase(_BaseModel):
    id_: Annotated[str, Alias("id")]
    library_id: Annotated[str, Alias("libraryId")]
    user_id: Annotated[str | None, Alias("userId")] = None
    name: str
    description: str | None = None
    cover_path: Annotated[str | None, Alias("coverPath")] = None
    last_update: Annotated[int, Alias("lastUpdate")]  # ms epoch
    created_at: Annotated[int, Alias("createdAt")]  # ms epoch


@dataclass(kw_only=True)
class Playlist(_PlaylistBase):
    """Playlist."""

    items: list[PlaylistItem]


@dataclass(kw_only=True)
class PlaylistExpanded(_PlaylistBase):
    """Playlist."""

    items: list[PlaylistItemExpanded]
