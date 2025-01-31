"""Schema for playlist."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias, Discriminator

from aioaudiobookshelf.schema.podcast import PodcastEpisodeExpanded

from . import _BaseModel
from .library import LibraryItemExpandedBook, LibraryItemMinifiedPodcast


@dataclass
class PlaylistItem(_BaseModel):
    """PlaylistItem."""

    library_item_id: Annotated[str, Alias("libraryItemId")]
    episode_id: Annotated[str | None, Alias("episodeId")]


@dataclass
class PlaylistItemExpanded(_BaseModel):
    """PlaylistExpanded."""

    class Config(PlaylistItem.Config):
        """Config."""

        # can't use field as episode_id is either existing or not.
        discriminator = Discriminator(
            include_subtypes=True,
        )


@dataclass
class PlaylistItemExpandedBook(PlaylistItemExpanded):
    """PlaylistExpanded."""

    library_item: Annotated[LibraryItemExpandedBook, Alias("libraryItem")]


@dataclass
class PlaylistItemExpandedPodcast(PlaylistItemExpanded):
    """PlaylistItemExpandedPodcast."""

    library_item: Annotated[LibraryItemMinifiedPodcast, Alias("libraryItem")]
    episode_id: Annotated[str, Alias("episodeId")]
    episode: PodcastEpisodeExpanded


@dataclass
class _PlaylistBase(_BaseModel):
    id_: Annotated[str, Alias("id")]
    library_id: Annotated[str, Alias("libraryId")]
    # this is missing
    # user_id: Annotated[str, Alias("userId")]
    name: str
    description: str | None
    # this is missing
    # cover_path: Annotated[str | None, Alias("coverPath")]
    last_update: Annotated[int, Alias("lastUpdate")]  # ms epoch
    created_at: Annotated[int, Alias("createdAt")]  # ms epoch


@dataclass
class Playlist(_PlaylistBase):
    """Playlist."""

    items: list[PlaylistItem]


@dataclass
class PlaylistExpanded(_PlaylistBase):
    """Playlist."""

    items: list[PlaylistItemExpanded]
