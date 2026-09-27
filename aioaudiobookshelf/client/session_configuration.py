"""Session Configuration."""

import asyncio
import logging
from dataclasses import dataclass

from aiohttp.client import DEFAULT_TIMEOUT, ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientConnectionError, ClientResponseError

from aioaudiobookshelf.exceptions import (
    AbsError,
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
    timeout: ClientTimeout = DEFAULT_TIMEOUT
    logger: logging.Logger | None = None

    @property
    def headers(self) -> dict[str, str]:
        """Session headers.

        These are normal request headers.
        """
        # the access token wins, as in BaseClient.token, so both name the same token
        if self.access_token is not None:
            return {"Authorization": f"Bearer {self.access_token}"}
        if self.token is not None:
            return {"Authorization": f"Bearer {self.token}"}
        raise TokenIsMissingError("Token not set.")

    @property
    def headers_refresh_logout(self) -> dict[str, str]:
        """Session headers for /auth/refresh and /logout.

        Only v2.26 and above.
        """
        if self.refresh_token is None:
            raise TokenIsMissingError("Refresh token not set.")
        return {"x-refresh-token": self.refresh_token}

    @property
    def cookies_refresh_logout(self) -> dict[str, str]:
        """Cookie for /auth/refresh and /logout.

        On /logout abs reads `req.cookies.refresh_token || req.headers['x-refresh-token']`
        (Auth.js), so a cookie jar shared with another client of the same server would
        end that client's session instead of ours. On /auth/refresh the header wins,
        which was never at risk; we send the cookie there too so both stay in step.
        """
        if self.refresh_token is None:
            raise TokenIsMissingError("Refresh token not set.")
        return {"refresh_token": self.refresh_token}

    def __post_init__(self) -> None:
        """Post init."""
        self.url = self.url.rstrip("/")
        self.__refresh_lock = asyncio.Lock()
        self.__refresh_generation = 0
        self.__refresh_error: AbsError | None = None

    async def refresh(self) -> None:
        """Refresh access_token with refresh token.

        Callers which arrive during a running refresh wait for it and share its
        outcome, instead of sending a request of their own.

        v2.26 and above
        """
        generation = self.__refresh_generation
        async with self.__refresh_lock:
            if generation != self.__refresh_generation:
                # refreshed or authenticated by a concurrent caller
                if self.__refresh_error is not None:
                    raise self.__refresh_error
                return
            self.__refresh_error = None
            try:
                await self._request_new_tokens()
            except AbsError as err:
                self.__refresh_error = err
                raise
            finally:
                # only now callers which entered before are done waiting
                self.__refresh_generation += 1

    async def _request_new_tokens(self) -> None:
        try:
            endpoint = "auth/refresh"
            response = await self.session.post(
                f"{self.url}/{endpoint}",
                ssl=self.verify_ssl,
                headers=self.headers_refresh_logout,
                cookies=self.cookies_refresh_logout,
                raise_for_status=True,
                timeout=self.timeout,
            )
        except (ClientConnectionError, TimeoutError) as err:
            raise ServiceUnavailableError from err
        except ClientResponseError as err:
            if err.status == 401:
                raise RefreshTokenExpiredError from err
            # e.g. abs' rate limit, or a proxy while abs restarts
            raise ServiceUnavailableError from err
        data = await response.read()
        # a SchemaError from here means abs answered without the tokens we asked for
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
                self.access_token = None
                self.refresh_token = None
            else:
                assert login_response.user.refresh_token is not None
                self.access_token = login_response.user.access_token
                self.refresh_token = login_response.user.refresh_token
                # a server which now issues access tokens does not accept the old one
                self.token = None
            # a refresh waiting for this lock shares the new tokens
            self.__refresh_error = None
            self.__refresh_generation += 1
