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
    size: int  # in bytes
    modified_time_ms: Annotated[int, Alias("mtimeMs")]
    changed_time_ms: Annotated[int, Alias("ctimeMs")]
    created_time_ms: Annotated[int, Alias("birthtimeMs")] = 0  # 0 if unknown
