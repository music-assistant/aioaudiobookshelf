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
