"""User schema."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel
from .audio import AudioBookmark
from .media_progress import MediaProgress


@dataclass(kw_only=True)
class UserPermissions(_BaseModel):
    """UserPermissions. No variants.

    https://api.audiobookshelf.org/#user-permissions
    """

    download: bool
    update: bool
    delete: bool
    upload: bool
    access_all_libraries: Annotated[bool, Alias("accessAllLibraries")]
    access_all_tags: Annotated[bool, Alias("accessAllTags")]
    access_explicit_content: Annotated[bool, Alias("accessExplicitContent")]


class UserType(StrEnum):
    """UserType."""

    ROOT = "root"  # is the very first user of the server
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


@dataclass(kw_only=True)
class _UserBase(_BaseModel):
    """Shared attributes for User.

    https://api.audiobookshelf.org/#user
    """

    id_: Annotated[str, Alias("id")]
    username: str
    type_: Annotated[UserType, Alias("type")]


@dataclass(kw_only=True)
class User(_UserBase):
    """User."""

    # see https://github.com/advplyr/audiobookshelf/discussions/4460
    # new in v2.26.0 old token system will be removed in the future
    # we make them optional to have some backwards compatibility
    token: str | None = None
    # will only be returned if x-return-tokens is set to true in header
    refresh_token: Annotated[str | None, Alias("refreshToken")] = None
    access_token: Annotated[str | None, Alias("accessToken")] = None

    media_progress: Annotated[list[MediaProgress], Alias("mediaProgress")]
    series_hide_from_continue_listening: Annotated[
        list[str], Alias("seriesHideFromContinueListening")
    ]
    bookmarks: list[AudioBookmark]
    is_active: Annotated[bool, Alias("isActive")]
    is_locked: Annotated[bool, Alias("isLocked")]
    last_seen: Annotated[int | None, Alias("lastSeen")] = None
    created_at: Annotated[int, Alias("createdAt")]
    permissions: UserPermissions
    # empty = all accessible
    libraries_accessible: Annotated[list[str], Alias("librariesAccessible")] = field(
        default_factory=list
    )

    # is apparently omitted if empty
    # empty = all accessible
    item_tags_accessible: Annotated[list[str], Alias("itemTagsAccessible")] = field(
        default_factory=list
    )


# not yet added:
# UserWithProgressDetails
# UserWithSession
