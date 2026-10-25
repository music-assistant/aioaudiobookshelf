"""Params and responses for sessions."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel


@dataclass(kw_only=True)
class CloseOpenSessionsParameters(_BaseModel):
    """CloseOpenSessionsParameters."""

    current_time: Annotated[float, Alias("currentTime")]
    time_listened: Annotated[float, Alias("timeListened")]
    duration: float


SyncOpenSessionParameters = CloseOpenSessionsParameters


@dataclass(kw_only=True)
class LocalSessionSyncResult(_BaseModel):
    """LocalSessionSyncResult, see abs' managers/PlaybackSessionManager.js."""

    id_: Annotated[str, Alias("id")]
    success: bool
    error: str | None = None
    progress_synced: Annotated[bool, Alias("progressSynced")] = False


@dataclass(kw_only=True)
class SyncLocalSessionsResponse(_BaseModel):
    """SyncLocalSessionsResponse."""

    results: list[LocalSessionSyncResult]
