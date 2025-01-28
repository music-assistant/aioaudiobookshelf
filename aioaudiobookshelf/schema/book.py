"""Schema for Books."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .audio import AudioTrack
from .author import AuthorMinified
from .file import EBookFile
from .series import SeriesSequence


@dataclass
class BookChapter(_BaseModel):
    """
    BookChapter. No variants.

    https://api.audiobookshelf.org/#book-chapter
    """

    id_: Annotated[int, Alias("id")]
    start: float
    end: float
    title: str


@dataclass
class _BookMetadataBase(_BaseModel):
    """_BookMetadataBase."""

    title: str | None
    subtitle: str | None
    genres: list[str]
    published_year: Annotated[str | None, Alias("publishedYear")]
    published_date: Annotated[str | None, Alias("publishedDate")]
    publisher: str | None
    description: str | None
    isbn: str | None
    asin: str | None
    language: str | None
    explicit: bool


@dataclass
class BookMetadata(_BookMetadataBase):
    """BookMetadata."""

    authors: list[AuthorMinified]
    narrators: list[str]
    series: list[SeriesSequence]


@dataclass
class BookMetadataMinified(_BookMetadataBase):
    """BookMetadataMinified."""

    title_ignore_prefix: Annotated[str, Alias("titleIgnorePrefix")]
    author_name: Annotated[str, Alias("authorName")]
    author_name_lf: Annotated[str, Alias("authorNameLF")]
    narrator_name: Annotated[str, Alias("narratorName")]
    series_name: Annotated[str, Alias("seriesName")]


@dataclass
class BookMetadataExpanded(BookMetadata, BookMetadataMinified):
    """BookMetadataExpanded."""


@dataclass
class _BookBase(_BaseModel):
    """_BookBase."""

    tags: list[str]
    cover_path: Annotated[str | None, Alias("coverPath")]


@dataclass
class Book(_BookBase):
    """Book."""

    library_item_id: Annotated[str, Alias("libraryItemId")]
    metadata: BookMetadata
    # audio_files: Annotated[list[AudioFile], Alias("audioFiles")]
    chapters: list[BookChapter]
    ebook_file: Annotated[EBookFile | None, Alias("ebookFile")]


@dataclass
class BookMinified(_BookBase):
    """BookMinified."""

    metadata: BookMetadataMinified
    num_tracks: Annotated[int, Alias("numTracks")]
    num_audiofiles: Annotated[int, Alias("numAudioFiles")]
    num_chapters: Annotated[int, Alias("numChapters")]
    duration: float  # in s
    size: int  # in bytes
    ebook_format: Annotated[str | None, Alias("ebookFormat")]


@dataclass
class BookExpanded(_BookBase):
    """BookExpanded."""

    library_item_id: Annotated[str, Alias("libraryItemId")]
    metadata: BookMetadataExpanded
    # audio_files: Annotated[list[AudioFile], Alias("audioFiles")]
    chapters: list[BookChapter]
    ebook_file: Annotated[EBookFile | None, Alias("ebookFile")]
    duration: float
    size: int  # bytes
    tracks: list[AudioTrack]
