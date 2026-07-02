"""File schema."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel


@dataclass(kw_only=True)
class FileMetadata(_BaseModel):
    """FileMetadata."""

    filename: str
    ext: str
    path: str
    relative_path: Annotated[str, Alias("relPath")]
    size: int | None = None  # in bytes
    # might not be present, see https://github.com/music-assistant/support/issues/3914
    modified_time_ms: Annotated[int | None, Alias("mtimeMs")] = None
    changed_time_ms: Annotated[int | None, Alias("ctimeMs")]
    created_time_ms: Annotated[int | None, Alias("birthtimeMs")] = 0  # 0 if unknown
