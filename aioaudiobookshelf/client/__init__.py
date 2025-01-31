"""Clients for Audiobookshelf."""

from aioaudiobookshelf.exceptions import BadUserError
from aioaudiobookshelf.schema.user import UserType

from .collections_ import CollectionsClient
from .items import ItemsClient
from .libraries import LibrariesClient
from .playlists import PlaylistsClient


class UserClient(LibrariesClient, ItemsClient, CollectionsClient, PlaylistsClient):
    """Client which uses endpoints accessible to a user."""

    def _verify_user(self) -> None:
        if self.user.type_ not in [UserType.ADMIN, UserType.ROOT, UserType.USER]:
            raise BadUserError


class AdminClient(UserClient):
    """Client which uses endpoints accessible to users and admins."""

    def _verify_user(self) -> None:
        if self.user.type_ not in [UserType.ADMIN, UserType.ROOT]:
            raise BadUserError
