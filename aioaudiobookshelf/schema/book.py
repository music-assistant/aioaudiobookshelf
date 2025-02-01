"""Schema for Books."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .audio import AudioFile, AudioTrack
from .author import AuthorMinified
from .file import FileMetadata
from .series import SeriesSequence


@dataclass(kw_only=True)
class EBookFile(_BaseModel):
    """EBookFile."""

    ino: str
    metadata: FileMetadata
    ebook_format: Annotated[str, Alias("ebookFormat")]
    added_at: Annotated[int, Alias("addedAt")]  # time in ms since unix epoch
    updated_at: Annotated[int, Alias("updatedAt")]  # time in ms since unix epoch


@dataclass(kw_only=True)
class BookChapter(_BaseModel):
    """
    BookChapter. No variants.

    https://api.audiobookshelf.org/#book-chapter
    """

    id_: Annotated[int, Alias("id")]
    start: float
    end: float
    title: str


@dataclass(kw_only=True)
class _BookMetadataBase(_BaseModel):
    """_BookMetadataBase."""

    title: str | None = None
    subtitle: str | None = None
    genres: list[str]
    published_year: Annotated[str | None, Alias("publishedYear")] = None
    published_date: Annotated[str | None, Alias("publishedDate")] = None
    publisher: str | None = None
    description: str | None = None
    isbn: str | None = None
    asin: str | None = None
    language: str | None = None
    explicit: bool


@dataclass(kw_only=True)
class BookMetadata(_BookMetadataBase):
    """BookMetadata."""

    authors: list[AuthorMinified]
    narrators: list[str]
    series: list[SeriesSequence]


@dataclass(kw_only=True)
class BookMetadataMinified(_BookMetadataBase):
    """BookMetadataMinified."""

    title_ignore_prefix: Annotated[str, Alias("titleIgnorePrefix")]
    author_name: Annotated[str, Alias("authorName")]
    author_name_lf: Annotated[str, Alias("authorNameLF")]
    narrator_name: Annotated[str, Alias("narratorName")]
    series_name: Annotated[str, Alias("seriesName")]


@dataclass(kw_only=True)
class BookMetadataExpanded(BookMetadata, BookMetadataMinified):
    """BookMetadataExpanded."""


@dataclass(kw_only=True)
class _BookBase(_BaseModel):
    """_BookBase."""

    tags: list[str]
    cover_path: Annotated[str | None, Alias("coverPath")] = None


@dataclass(kw_only=True)
class Book(_BookBase):
    """Book."""

    library_item_id: Annotated[str, Alias("libraryItemId")]
    metadata: BookMetadata
    audio_files: Annotated[list[AudioFile], Alias("audioFiles")]
    chapters: list[BookChapter]
    ebook_file: Annotated[EBookFile | None, Alias("ebookFile")] = None


@dataclass(kw_only=True)
class BookMinified(_BookBase):
    """BookMinified."""

    metadata: BookMetadataMinified
    num_tracks: Annotated[int, Alias("numTracks")]
    num_audiofiles: Annotated[int, Alias("numAudioFiles")]
    num_chapters: Annotated[int, Alias("numChapters")]
    duration: float  # in s
    size: int  # in bytes
    ebook_format: Annotated[str | None, Alias("ebookFormat")] = None


@dataclass(kw_only=True)
class BookExpanded(_BookBase):
    """BookExpanded."""

    library_item_id: Annotated[str, Alias("libraryItemId")]
    metadata: BookMetadataExpanded
    audio_files: Annotated[list[AudioFile], Alias("audioFiles")]
    chapters: list[BookChapter]
    ebook_file: Annotated[EBookFile | None, Alias("ebookFile")] = None
    duration: float
    size: int  # bytes
    tracks: list[AudioTrack]
