"""BaseClient."""

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from aiohttp.client_exceptions import ClientResponseError

if TYPE_CHECKING:
    from aioaudiobookshelf.client import SessionConfiguration
from aioaudiobookshelf.exceptions import ApiError
from aioaudiobookshelf.schema.calls_login import LoginResponse


class BaseClient:
    """Base for clients."""

    def __init__(
        self, session_config: "SessionConfiguration", login_response: LoginResponse
    ) -> None:
        self.session_config = session_config
        self.user = login_response.user
        if not self.session_config.token:
            self.session_config.token = login_response.user.token
        self._token = self.session_config.token

        if self.session_config.logger is None:
            self.logger = logging.getLogger(__name__)
            logging.basicConfig()
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger = self.session_config.logger

        self.logger.debug(
            "Initialized client %s",
            self.__class__.__name__,
        )

        self._verify_user()

    @property
    def token(self) -> str:
        return self._token

    @abstractmethod
    def _verify_user(self) -> None:
        """Verify if user has enough permissions for endpoints in use."""

    async def _post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> bytes:
        """POST request to abs api."""
        try:
            response = await self.session_config.session.post(
                f"{self.session_config.url}/{endpoint}",
                json=data,
                ssl=self.session_config.verify_ssl,
                headers=self.session_config.headers,
                raise_for_status=True,
            )
        except ClientResponseError as exc:
            raise ApiError(f"API POST call to {endpoint} failed.") from exc
        return await response.read()

    async def _get(self, endpoint: str, params: dict[str, str | int] | None = None) -> bytes:
        """GET request to abs api."""
        response = await self.session_config.session.get(
            f"{self.session_config.url}/{endpoint}",
            params=params,
            ssl=self.session_config.verify_ssl,
            headers=self.session_config.headers,
        )
        status = response.status
        if response.content_type == "application/json" and status == 200:
            return await response.read()
        if status == 404:
            return b""
        raise ApiError(f"API GET call to {endpoint} failed.")

    async def _patch(self, endpoint: str, data: dict[str, Any] | None = None) -> None:
        """PATCH request to abs api."""
        try:
            await self.session_config.session.patch(
                f"{self.session_config.url}/{endpoint}",
                json=data,
                ssl=self.session_config.verify_ssl,
                headers=self.session_config.headers,
                raise_for_status=True,
            )
        except ClientResponseError as exc:
            raise ApiError(f"API PATCH call to {endpoint} failed.") from exc

    async def _delete(self, endpoint: str) -> None:
        """DELETE request to abs api."""
        try:
            await self.session_config.session.delete(
                f"{self.session_config.url}/{endpoint}",
                ssl=self.session_config.verify_ssl,
                headers=self.session_config.headers,
                raise_for_status=True,
            )
        except ClientResponseError as exc:
            raise ApiError(f"API DELETE call to {endpoint} failed.") from exc

    async def logout(self) -> None:
        """Logout client."""
        await self._post("logout")
