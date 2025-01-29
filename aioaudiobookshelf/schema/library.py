"""Library Schema."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated

from mashumaro.types import Alias, Discriminator

from . import _BaseModel
from .book import Book, BookExpanded, BookMinified
from .file import FileMetadata
from .folder import Folder
from .podcast import Podcast, PodcastExpanded, PodcastMinified


class LibraryIcons(StrEnum):
    """LibraryIcons."""

    DATABASE = "database"
    AUDIOBOOKSHELF = "audiobookshelf"
    BOOKS_1 = "books-1"
    BOOKS_2 = "books-2"
    BOOK_1 = "book-1"
    MICROPHONE_1 = "microphone-1"
    MICROPHONE_3 = "microphone-3"
    RADIO = "radio"
    PODCAST = "podcast"
    RSS = "rss"
    HEADPHONES = "headphones"
    MUSIC = "music"
    FILE_PICTURE = "file-picture"
    ROCKET = "rocket"
    POWER = "power"
    START = "star"
    HEART = "heart"


class LibraryMediaType(StrEnum):
    """LibraryMediaType."""

    BOOK = "book"
    PODCAST = "podcast"


@dataclass
class LibraryFile(_BaseModel):
    """LibraryFile."""

    ino: str
    metadata: FileMetadata
    added_at: Annotated[int, Alias("addedAt")]  # ms epoch
    updated_at: Annotated[int, Alias("updatedAt")]  # ms epoch
    file_type: Annotated[str, Alias("fileType")]


@dataclass
class LibrarySettings(_BaseModel):
    """LibrarySettings."""

    cover_aspect_ratio: Annotated[int, Alias("coverAspectRatio")]
    disable_watcher: Annotated[bool, Alias("disableWatcher")]
    skip_matching_media_with_asin: Annotated[bool, Alias("skipMatchingMediaWithAsin")]
    skip_matching_media_with_isbn: Annotated[bool, Alias("skipMatchingMediaWithIsbn")]
    auto_scan_cron_expression: Annotated[str | None, Alias("autoScanCronExpression")]


@dataclass
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


@dataclass
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


@dataclass
class LibraryItem(_LibraryItemBase):
    """LibraryItem."""

    class Config(_LibraryItemBase.Config):
        """Config."""

        discriminator = Discriminator(
            field="media_type",
            include_subtypes=True,
        )

    last_scan: Annotated[int | None, Alias("lastScan")]  # ms epoch
    scan_version: Annotated[str | None, Alias("scanVersion")]
    library_files: Annotated[list[LibraryFile], Alias("libraryFiles")]


@dataclass
class LibraryItemBook(LibraryItem):
    """LibraryItemBook."""

    media: Book
    media_type: Annotated[LibraryMediaType, Alias("mediaType")] = LibraryMediaType.BOOK


@dataclass
class LibraryItemPodcast(LibraryItem):
    """LibraryItemPodcast."""

    media: Podcast
    media_type: Annotated[LibraryMediaType, Alias("mediaType")] = LibraryMediaType.PODCAST


@dataclass
class LibraryItemMinified(_LibraryItemBase):
    """LibraryItemMinified."""

    class Config(_LibraryItemBase.Config):
        """Config."""

        discriminator = Discriminator(
            field="media_type",
            include_subtypes=True,
        )

    num_files: Annotated[int, Alias("numFiles")]
    size: int


@dataclass
class LibraryItemMinifiedBook(LibraryItemMinified):
    """LibraryItemMinifiedBook."""

    media: BookMinified
    media_type: Annotated[LibraryMediaType, Alias("mediaType")] = LibraryMediaType.BOOK


@dataclass
class LibraryItemMinifiedPodcast(LibraryItemMinified):
    """LibraryItemMinifiedPodcast."""

    media: PodcastMinified
    media_type: Annotated[LibraryMediaType, Alias("mediaType")] = LibraryMediaType.PODCAST


@dataclass
class LibraryItemExpanded(LibraryItem):
    """LibraryItemExpanded."""

    class Config(LibraryItem.Config):
        """Config."""

        discriminator = Discriminator(
            field="media_type",
            include_subtypes=True,
        )

    size: int


@dataclass
class LibraryItemExpandedBook(LibraryItemExpanded):
    """LibraryItemExpandedBook."""

    media: BookExpanded
    media_type: Annotated[LibraryMediaType, Alias("mediaType")] = LibraryMediaType.BOOK


@dataclass
class LibraryItemExpandedPodcast(LibraryItemExpanded):
    """LibraryItemExpandedPodcast."""

    media: PodcastExpanded
    media_type: Annotated[LibraryMediaType, Alias("mediaType")] = LibraryMediaType.PODCAST
