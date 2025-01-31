"""Clients for Audiobookshelf."""

from dataclasses import dataclass

from aiohttp import ClientSession

from aioaudiobookshelf.exceptions import BadUserError
from aioaudiobookshelf.schema.user import UserType

from .authors import AuthorsClient
from .collections_ import CollectionsClient
from .items import ItemsClient
from .libraries import LibrariesClient
from .me import MeClient
from .playlists import PlaylistsClient
from .series import SeriesClient
from .session import SessionsClient


@dataclass(kw_only=True)
class SessionConfiguration:
    """Session configuration for abs client."""

    session: ClientSession
    url: str
    verify_ssl: bool = True
    token: str | None = None
    pagination_items_per_page: int = 10

    @property
    def headers(self) -> dict[str, str]:
        """Session headers."""
        if self.token is None:
            raise RuntimeError("Token not set.")
        return {"Authorization": f"Bearer {self.token}"}

    def __post_init__(self) -> None:
        """Post init."""
        self.url = self.url.rstrip("/")


class UserClient(
    LibrariesClient,
    ItemsClient,
    CollectionsClient,
    PlaylistsClient,
    MeClient,
    AuthorsClient,
    SeriesClient,
    SessionsClient,
):
    """Client which uses endpoints accessible to a user."""

    def _verify_user(self) -> None:
        if self.user.type_ not in [UserType.ADMIN, UserType.ROOT, UserType.USER]:
            raise BadUserError


class AdminClient(UserClient):
    """Client which uses endpoints accessible to users and admins."""

    def _verify_user(self) -> None:
        if self.user.type_ not in [UserType.ADMIN, UserType.ROOT]:
            raise BadUserError
