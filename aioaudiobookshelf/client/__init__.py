"""Clients for Audiobookshelf."""

from aioaudiobookshelf.exceptions import BadUserError
from aioaudiobookshelf.schema.user import UserType

from .libraries import LibrariesClient


class UserClient(LibrariesClient):
    """Client which uses endpoints accessible to a user."""

    def _verify_user(self) -> None:
        if self.user.type_ not in [UserType.ADMIN, UserType.ROOT, UserType.USER]:
            raise BadUserError


class AdminClient(UserClient):
    """Client which uses endpoints accessible to users and admins."""

    def _verify_user(self) -> None:
        if self.user.type_ not in [UserType.ADMIN, UserType.ROOT]:
            raise BadUserError
