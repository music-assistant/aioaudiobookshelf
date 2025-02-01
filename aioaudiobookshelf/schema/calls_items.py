"""Calls for items."""

from dataclasses import dataclass, field
from typing import Annotated

from mashumaro.types import Alias

from aioaudiobookshelf.schema import _BaseModel
from aioaudiobookshelf.schema.session import DeviceInfo


@dataclass(kw_only=True)
class PlayParameters(_BaseModel):
    """PlayParameters.

    https://api.audiobookshelf.org/#play-a-library-item-or-podcast-episode
    """

    device_info: Annotated[DeviceInfo, Alias("deviceInfo")]
    force_direct_play: Annotated[bool, Alias("forceDirectPlay")] = False
    force_transcode: Annotated[bool, Alias("forceTranscode")] = False
    supported_mime_types: Annotated[list[str], Alias("supportedMimeTypes")] = field(
        default_factory=list
    )
    media_player: Annotated[str, Alias("mediaPlayer")] = "unknown"


PlaybackSessionParameters = PlayParameters
