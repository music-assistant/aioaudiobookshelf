"""Clients for Audiobookshelf."""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from aiohttp import ClientSession

from .exceptions import BadUserError
from .schema.requests import LoginResponse
from .schema.user import UserType


@dataclass(kw_only=True)
class SessionConfiguration:
    """Session configuration for abs client."""

    session: ClientSession
    url: str
    verify_ssl: bool = True
    token: str | None = None

    @property
    def headers(self) -> dict[str, str]:
        """Session headers."""
        if self.token is None:
            raise RuntimeError("Token not set.")
        return {"Authorization": f"Bearer {self.token}"}


class _BaseClient:
    """Base for clients."""

    def __init__(self, session_config: SessionConfiguration, login_response: LoginResponse) -> None:
        self.session_config = session_config
        self.user = login_response.user
        if self.session_config.token is None:
            self.session_config.token = login_response.user.token

        self._verify_user()

    @abstractmethod
    def _verify_user(self) -> None:
        """Verify if user has enough permissions for endpoints in use."""

    async def _post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> bytes:
        """POST request to abs api."""
        response = await self.session_config.session.post(
            f"{self.session_config.url}/{endpoint}",
            json=data,
            ssl=self.session_config.verify_ssl,
            headers=self.session_config.headers,
        )
        return await response.read()

    async def logout(self) -> None:
        """Logout client."""
        await self._post("logout")


class UserClient(_BaseClient):
    """Client which uses endpoints accessible to a user."""

    def _verify_user(self) -> None:
        if self.user.type_ not in [UserType.ADMIN, UserType.ROOT, UserType.USER]:
            raise BadUserError


class AdminClient(UserClient):
    """Client which uses endpoints accessible to users and admins."""

    def _verify_user(self) -> None:
        if self.user.type_ not in [UserType.ADMIN, UserType.ROOT]:
            raise BadUserError
