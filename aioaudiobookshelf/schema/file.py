"""File schema."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel


@dataclass
class FileMetadata(_BaseModel):
    """FileMetadata."""

    filename: str
    ext: str
    path: str
    relative_path: Annotated[str, Alias("relPath")]
    size: int  # in bytes
    modified_time_ms: Annotated[int, Alias("mtimeMs")]
    changed_time_ms: Annotated[int, Alias("ctimeMs")]
    created_time_ms: Annotated[int, Alias("birthtimeMs")] = 0  # 0 if unknown


@dataclass
class EBookFile(_BaseModel):
    """EBookFile."""

    ino: str
    metadata: FileMetadata
    ebook_format: Annotated[str, Alias("ebookFormat")]
    added_at: Annotated[int, Alias("addedAt")]  # time in ms since unix epoch
    updated_at: Annotated[int, Alias("updatedAt")]  # time in ms since unix epoch
