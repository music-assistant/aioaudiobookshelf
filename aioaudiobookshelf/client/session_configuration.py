"""Session Configuration."""

import asyncio
import logging
from dataclasses import dataclass

from aiohttp.client import ClientSession
from aiohttp.client_exceptions import ClientResponseError

from aioaudiobookshelf.exceptions import (
    RefreshTokenExpiredError,
    ServiceUnavailableError,
    TokenIsMissingError,
)
from aioaudiobookshelf.helpers import get_login_response
from aioaudiobookshelf.schema.calls_login import RefreshResponse


@dataclass(kw_only=True)
class SessionConfiguration:
    """Session configuration for abs client.

    Relevant token information for v2.26 and above:
        https://github.com/advplyr/audiobookshelf/discussions/4460
    """

    session: ClientSession
    url: str
    verify_ssl: bool = True
    token: str | None = None  # pre v2.26 token or api token if > v2.26
    access_token: str | None = None  # > v2.26
    refresh_token: str | None = None  # > v2.26
    auto_refresh: bool = True  # automatically refresh access token, should it be expired.
    pagination_items_per_page: int = 10
    logger: logging.Logger | None = None

    @property
    def headers(self) -> dict[str, str]:
        """Session headers.

        These are normal request headers.
        """
        if self.token is not None:
            return {"Authorization": f"Bearer {self.token}"}
        if self.access_token is not None:
            return {"Authorization": f"Bearer {self.access_token}"}
        raise TokenIsMissingError("Token not set.")

    @property
    def headers_refresh_logout(self) -> dict[str, str]:
        """Session headers for /auth/refresh and /logout.

        Only v2.26 and above.
        """
        if self.refresh_token is None:
            raise TokenIsMissingError("Refresh token not set.")
        return {"x-refresh-token": self.refresh_token}

    def __post_init__(self) -> None:
        """Post init."""
        self.url = self.url.rstrip("/")
        self.__refresh_lock = asyncio.Lock()

    async def refresh(self) -> None:
        """Refresh access_token with refresh token.

        v2.26 and above
        """
        if self.__refresh_lock.locked():
            return
        async with self.__refresh_lock:
            try:
                endpoint = "auth/refresh"
                response = await self.session.post(
                    f"{self.url}/{endpoint}",
                    ssl=self.verify_ssl,
                    headers=self.headers_refresh_logout,
                    raise_for_status=True,
                )
            except ClientResponseError as err:
                if err.code == 503:
                    raise ServiceUnavailableError from err
                raise RefreshTokenExpiredError from err
            data = await response.read()
            refresh_response = RefreshResponse.from_json(data)
            assert refresh_response.user.access_token is not None
            assert refresh_response.user.refresh_token is not None
            self.access_token = refresh_response.user.access_token
            self.refresh_token = refresh_response.user.refresh_token

    async def authenticate(self, *, username: str, password: str) -> None:
        """Relogin and update tokens if refresh token expired."""
        async with self.__refresh_lock:
            login_response = await get_login_response(
                session_config=self, username=username, password=password
            )
            if login_response.user.access_token is None:
                # pre v2.26
                assert login_response.user.token is not None
                self.token = login_response.user.token
                return
            assert login_response.user.access_token is not None
            assert login_response.user.refresh_token is not None
            self.access_token = login_response.user.access_token
            self.refresh_token = login_response.user.refresh_token
