"""Scheme for socket client."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .media_progress import MediaProgress


@dataclass(kw_only=True)
class UserItemProgressUpdatedEvent(_BaseModel):
    """UserItemProgressUpdatedEvent."""

    id_: Annotated[str, Alias("id")]
    data: MediaProgress
