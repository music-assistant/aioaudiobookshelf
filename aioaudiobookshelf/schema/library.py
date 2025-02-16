"""Library Schema."""
# Discriminators don't work together with aliases.
# https://github.com/Fatal1ty/mashumaro/issues/254
# ruff: noqa: N815

from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated

from mashumaro.types import Alias, Discriminator

from aioaudiobookshelf.schema.author import AuthorMinified
from aioaudiobookshelf.schema.series import SeriesFilterData

from . import _BaseModel
from .book import Book, BookExpanded, BookMinified
from .file import FileMetadata
from .folder import Folder
from .podcast import Podcast, PodcastExpanded, PodcastMinified


class LibraryIcons(StrEnum):
    """LibraryIcons."""

    DATABASE = "database"
    AUDIOBOOKSHELF = "audiobookshelf"
    BOOKS1 = "books-1"
    BOOKS2 = "books-2"
    BOOK1 = "book-1"
    MICROPHONE1 = "microphone-1"
    MICROPHONE3 = "microphone-3"
    RADIO = "radio"
    PODCAST = "podcast"
    RSS = "rss"
    HEADPHONES = "headphones"
    MUSIC = "music"
    FILEPICTURE = "file-picture"
    ROCKET = "rocket"
    POWER = "power"
    START = "star"
    HEART = "heart"


class LibraryMediaType(StrEnum):
    """LibraryMediaType."""

    BOOK = "book"
    PODCAST = "podcast"


@dataclass(kw_only=True)
class LibraryFile(_BaseModel):
    """LibraryFile."""

    ino: str
    metadata: FileMetadata
    added_at: Annotated[int, Alias("addedAt")]  # ms epoch
    updated_at: Annotated[int, Alias("updatedAt")]  # ms epoch
    file_type: Annotated[str, Alias("fileType")]


@dataclass(kw_only=True)
class LibrarySettings(_BaseModel):
    """LibrarySettings."""

    cover_aspect_ratio: Annotated[int, Alias("coverAspectRatio")]
    disable_watcher: Annotated[bool, Alias("disableWatcher")]
    skip_matching_media_with_asin: Annotated[bool | None, Alias("skipMatchingMediaWithAsin")] = None
    skip_matching_media_with_isbn: Annotated[bool | None, Alias("skipMatchingMediaWithIsbn")] = None
    auto_scan_cron_expression: Annotated[str | None, Alias("autoScanCronExpression")] = None


@dataclass(kw_only=True)
class Library(_BaseModel):
    """Library."""

    id_: Annotated[str, Alias("id")]
    name: str
    folders: list[Folder]
    display_order: Annotated[int, Alias("displayOrder")]
    icon: LibraryIcons
    media_type: Annotated[LibraryMediaType, Alias("mediaType")]
    # TODO: add enum
    provider: str
    settings: LibrarySettings
    created_at: Annotated[int, Alias("createdAt")]  # ms epoch
    last_update: Annotated[int, Alias("lastUpdate")]  # ms epoch


@dataclass(kw_only=True)
class _LibraryItemBase(_BaseModel):
    id_: Annotated[str, Alias("id")]
    ino: str
    library_id: Annotated[str, Alias("libraryId")]
    folder_id: Annotated[str, Alias("folderId")]
    path: str
    relative_path: Annotated[str, Alias("relPath")]
    is_file: Annotated[bool, Alias("isFile")]
    modified_time_ms: Annotated[int, Alias("mtimeMs")]
    changed_time_ms: Annotated[int, Alias("ctimeMs")]
    created_time_ms: Annotated[int, Alias("birthtimeMs")]  # epoch
    added_at: Annotated[int, Alias("addedAt")]
    updated_at: Annotated[int, Alias("updatedAt")]  # ms epoch
    is_missing: Annotated[bool, Alias("isMissing")]
    is_invalid: Annotated[bool, Alias("isInvalid")]


@dataclass(kw_only=True)
class LibraryItem(_LibraryItemBase):
    """LibraryItem."""

    class Config(_LibraryItemBase.Config):
        """Config."""

        discriminator = Discriminator(
            field="mediaType",
            include_subtypes=True,
        )

    last_scan: Annotated[int | None, Alias("lastScan")] = None  # ms epoch
    scan_version: Annotated[str | None, Alias("scanVersion")] = None
    library_files: Annotated[list[LibraryFile], Alias("libraryFiles")]


@dataclass(kw_only=True)
class LibraryItemBook(LibraryItem):
    """LibraryItemBook."""

    media: Book
    mediaType: LibraryMediaType = LibraryMediaType.BOOK


@dataclass(kw_only=True)
class LibraryItemPodcast(LibraryItem):
    """LibraryItemPodcast."""

    media: Podcast
    mediaType: LibraryMediaType = LibraryMediaType.PODCAST


@dataclass(kw_only=True)
class LibraryItemMinified(_LibraryItemBase):
    """LibraryItemMinified."""

    class Config(_LibraryItemBase.Config):
        """Config."""

        discriminator = Discriminator(
            field="mediaType",
            include_subtypes=True,
        )

    num_files: Annotated[int, Alias("numFiles")]
    size: int


@dataclass(kw_only=True)
class LibraryItemMinifiedBook(LibraryItemMinified):
    """LibraryItemMinifiedBook."""

    media: BookMinified
    mediaType: LibraryMediaType = LibraryMediaType.BOOK
    # media_type: Annotated[LibraryMediaType, Alias("mediaType")] = LibraryMediaType.BOOK
    # media_type: LibraryMediaType = field(
    #     metadata=field_options(alias="mediaType"), default=LibraryMediaType.BOOK
    # )


@dataclass(kw_only=True)
class LibraryItemMinifiedPodcast(LibraryItemMinified):
    """LibraryItemMinifiedPodcast."""

    media: PodcastMinified
    mediaType: LibraryMediaType = LibraryMediaType.PODCAST
    # media_type: Annotated[LibraryMediaType, Alias("mediaType")] = LibraryMediaType.PODCAST
    # media_type: LibraryMediaType = field(
    #     metadata=field_options(alias="mediaType"), default=LibraryMediaType.PODCAST
    # )


@dataclass(kw_only=True)
class LibraryItemExpanded(LibraryItem):
    """LibraryItemExpanded."""

    class Config(LibraryItem.Config):
        """Config."""

        discriminator = Discriminator(
            field="mediaType",
            include_subtypes=True,
        )

    size: int


@dataclass(kw_only=True)
class LibraryItemExpandedBook(LibraryItemExpanded):
    """LibraryItemExpandedBook."""

    media: BookExpanded
    mediaType: LibraryMediaType = LibraryMediaType.BOOK


@dataclass(kw_only=True)
class LibraryItemExpandedPodcast(LibraryItemExpanded):
    """LibraryItemExpandedPodcast."""

    media: PodcastExpanded
    mediaType: LibraryMediaType = LibraryMediaType.PODCAST


@dataclass(kw_only=True)
class LibraryFilterData(_BaseModel):
    """LibraryFilterData."""

    authors: list[AuthorMinified]
    genres: list[str]
    tags: list[str]
    series: list[SeriesFilterData]
    narrators: list[str]
    languages: list[str]
