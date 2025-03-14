"""Schema for shelf, the response object to library's personalized view."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated

from mashumaro.types import Alias, Discriminator

from aioaudiobookshelf.schema.author import AuthorExpanded

from . import _BaseModel
from .library import LibraryItemMinified
from .podcast import PodcastEpisode
from .series import Series


class ShelfId(StrEnum):
    """ShelfId."""

    LISTEN_AGAIN = "listen-again"
    CONTINUE_LISTENING = "continue-listening"
    CONTINUE_SERIES = "continue-series"
    RECOMMENDED = "recommended"
    RECENTLY_ADDED = "recently-added"
    EPISODES_RECENTLY_ADDED = "episodes-recently-added"
    RECENT_SERIES = "recent-series"
    NEWEST_AUTHORS = "newest-authors"
    DISCOVER = "discover"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "ShelfId":  # noqa: ARG003
        # copied from music_assistant_models
        """Set default enum member if an unknown value is provided."""
        return cls.UNKNOWN


@dataclass(kw_only=True)
class ShelfLibraryItemMinified(LibraryItemMinified):
    """ShelfLibraryItemMinified.

    Beside using type, there is another distinction on which attributes
    are available based on the id. We allow ourselves the easy route
    here, and just make all of them optional.
    """

    # episode (type) and
    # id: continue-listening, listen-again, episodes-recently-added
    recent_episode: Annotated[PodcastEpisode | None, Alias("recentEpisode")] = None

    # id: continue-listening
    progress_last_update_ms: Annotated[int | None, Alias("progressLastUpdate")] = None

    # id: continue-series
    previous_book_in_progress_last_update_ms: Annotated[
        int | None, Alias("prevBookInProgressLastUpdate")
    ] = None
    # TODO: minified item has seriesSequence, which we currently ignore

    # id: recommended
    weight: float | None = None

    # id: listen-again
    finished_at_ms: Annotated[int | None, Alias("finishedAt")] = None


@dataclass(kw_only=True)
class LibraryItemMinifiedBookSeriesShelf(ShelfLibraryItemMinified):
    """LibraryItemMinifiedBookSeriesShelf."""

    # this appears not to be around?
    series_sequence: Annotated[str | int | None, Alias("seriesSequence")] = None


@dataclass(kw_only=True)
class SeriesShelf(Series):
    """SeriesShelf."""

    books: list[LibraryItemMinifiedBookSeriesShelf]
    in_progress: Annotated[bool | None, Alias("inProgress")] = None
    has_active_book: Annotated[bool | None, Alias("hasActiveBook")] = None
    hide_from_continue_listening: Annotated[bool | None, Alias("hideFromContinueListening")] = None
    book_in_progress_last_update_ms: Annotated[int | None, Alias("bookInProgressLastUpdate")] = None
    first_book_unread: Annotated[
        LibraryItemMinifiedBookSeriesShelf | None, Alias("firstBookUnread")
    ] = None


class ShelfType(StrEnum):
    """ShelfType."""

    BOOK = "book"
    SERIES = "series"
    AUTHORS = "authors"
    EPISODE = "episode"
    PODCAST = "podcast"


@dataclass(kw_only=True)
class _ShelfBase(_BaseModel):
    """Shelf."""

    id_: Annotated[ShelfId, Alias("id")]
    label: str
    label_string_key: Annotated[str, Alias("labelStringKey")]
    type_: Annotated[ShelfType, Alias("type")]
    category: str | None = None


@dataclass(kw_only=True)
class Shelf(_ShelfBase):
    """Shelf."""

    class Config(_ShelfBase.Config):
        """Config."""

        discriminator = Discriminator(
            field="type",
            include_subtypes=True,
        )


@dataclass(kw_only=True)
class ShelfBook(Shelf):
    """ShelfBook."""

    type = ShelfType.BOOK
    entities: list[ShelfLibraryItemMinified]


@dataclass(kw_only=True)
class ShelfPodcast(Shelf):
    """ShelfBook."""

    type = ShelfType.PODCAST
    entities: list[ShelfLibraryItemMinified]


@dataclass(kw_only=True)
class ShelfEpisode(Shelf):
    """ShelfBook."""

    type = ShelfType.EPISODE
    entities: list[ShelfLibraryItemMinified]


@dataclass(kw_only=True)
class ShelfAuthors(Shelf):
    """ShelfAuthor."""

    type = ShelfType.AUTHORS

    entities: list[AuthorExpanded]


@dataclass(kw_only=True)
class ShelfSeries(Shelf):
    """ShelfSeries."""

    type = ShelfType.SERIES
    entities: list[SeriesShelf]
