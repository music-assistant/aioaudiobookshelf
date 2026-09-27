"""BaseClient."""

import logging
from abc import abstractmethod
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiohttp.client import ClientResponse, ClientTimeout
from aiohttp.client_exceptions import ClientConnectionError, ClientResponseError

if TYPE_CHECKING:
    from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import (
    AccessTokenExpiredError,
    ApiError,
    NotFoundError,
    ServiceUnavailableError,
    TokenIsMissingError,
    TokenNotRenewableError,
)
from aioaudiobookshelf.schema.calls_login import LoginResponse

# logout is best effort, it must not stall a shutdown
LOGOUT_TIMEOUT = ClientTimeout(total=10)

# abs rejects an api key or a pre v2.26 token the same way it rejects an expired
# access token, but neither of them can be refreshed
NOT_RENEWABLE_MESSAGE = "Abs rejected the token and it cannot be refreshed."


async def _json_body(response: ClientResponse) -> bytes:
    """Read a json answer, or free the connection if there is none."""
    if response.content_type == "application/json" and response.status == 200:
        return await response.read()
    response.release()
    return b""


class BaseClient:
    """Base for clients."""

    def __init__(
        self, session_config: "SessionConfiguration", login_response: LoginResponse
    ) -> None:
        self.session_config = session_config
        self.user = login_response.user
        self.server_settings = login_response.server_settings

        if not self.session_config.token and not self.session_config.refresh_token:
            self.session_config.adopt_tokens(login_response)

        self.logger = self.session_config.logger or logging.getLogger(__name__)

        self.logger.debug(
            "Initialized client %s",
            self.__class__.__name__,
        )

        self._verify_user()

    @property
    def token(self) -> str:
        if self.session_config.access_token is not None:
            return self.session_config.access_token
        if self.session_config.token is None:
            raise TokenIsMissingError
        return self.session_config.token

    @abstractmethod
    def _verify_user(self) -> None:
        """Verify if user has enough permissions for endpoints in use."""

    async def _retry(
        self, request: Callable[[], Awaitable[ClientResponse]], error_message: str
    ) -> ClientResponse:
        """Repeat a request once the tokens were refreshed."""
        try:
            return await request()
        except (ClientConnectionError, TimeoutError) as err:
            raise ServiceUnavailableError from err
        except ClientResponseError as err:
            if err.status == 404:
                raise NotFoundError from err
            raise ApiError(error_message) from err

    async def _post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> bytes:
        """POST request to abs api."""

        async def _request() -> ClientResponse:
            return await self.session_config.session.post(
                self.session_config.url_for(endpoint),
                json=data,
                ssl=self.session_config.verify_ssl,
                headers=self.session_config.headers,
                raise_for_status=True,
                timeout=self.session_config.timeout,
            )

        try:
            response = await _request()
        except (ClientConnectionError, TimeoutError) as err:
            raise ServiceUnavailableError from err
        except ClientResponseError as exc:
            if exc.status == 401:
                if self.session_config.refresh_token is None:
                    raise TokenNotRenewableError(NOT_RENEWABLE_MESSAGE) from exc
                if self.session_config.auto_refresh:
                    self.logger.debug("Auto refreshing tokens.")
                    await self.refresh()
                    response = await self._retry(_request, f"API POST call to {endpoint} failed.")
                else:
                    raise AccessTokenExpiredError from exc
            elif exc.status == 404:
                raise NotFoundError from exc
            else:
                raise ApiError(f"API POST call to {endpoint} failed.") from exc

        return await response.read()

    async def _get(
        self,
        endpoint: str,
        params: dict[str, str | int] | None = None,
        *,
        json_response: bool = True,
    ) -> bytes:
        """GET request to abs api."""

        async def _request() -> ClientResponse:
            return await self.session_config.session.get(
                self.session_config.url_for(endpoint),
                params=params,
                ssl=self.session_config.verify_ssl,
                headers=self.session_config.headers,
                timeout=self.session_config.timeout,
            )

        try:
            response = await _request()
            if response.status == 401:
                if self.session_config.refresh_token is None:
                    response.release()
                    raise TokenNotRenewableError(NOT_RENEWABLE_MESSAGE)
                if not self.session_config.auto_refresh:
                    response.release()
                    raise AccessTokenExpiredError
                self.logger.debug("Auto refreshing tokens.")
                response.release()
                await self.refresh()
                response = await _request()
        except (ClientConnectionError, TimeoutError) as err:
            raise ServiceUnavailableError from err

        status = response.status
        if status == 200 and (not json_response or response.content_type == "application/json"):
            return await response.read()
        response.release()
        if status == 404:
            raise NotFoundError
        raise ApiError(f"API GET call to {endpoint} failed.")

    async def _patch(self, endpoint: str, data: dict[str, Any] | None = None) -> bytes:
        """PATCH request to abs api."""

        async def _request() -> ClientResponse:
            return await self.session_config.session.patch(
                self.session_config.url_for(endpoint),
                json=data,
                ssl=self.session_config.verify_ssl,
                headers=self.session_config.headers,
                raise_for_status=True,
                timeout=self.session_config.timeout,
            )

        try:
            response = await _request()
        except (ClientConnectionError, TimeoutError) as err:
            raise ServiceUnavailableError from err
        except ClientResponseError as exc:
            if exc.status == 401:
                if self.session_config.refresh_token is None:
                    raise TokenNotRenewableError(NOT_RENEWABLE_MESSAGE) from exc
                if self.session_config.auto_refresh:
                    self.logger.debug("Auto refreshing tokens.")
                    await self.refresh()
                    response = await self._retry(_request, f"API PATCH call to {endpoint} failed.")
                else:
                    raise AccessTokenExpiredError from exc
            elif exc.status == 404:
                raise NotFoundError from exc
            else:
                raise ApiError(f"API PATCH call to {endpoint} failed.") from exc
        return await _json_body(response)

    async def _delete(self, endpoint: str) -> bytes:
        """DELETE request to abs api."""

        async def _request() -> ClientResponse:
            return await self.session_config.session.delete(
                self.session_config.url_for(endpoint),
                ssl=self.session_config.verify_ssl,
                headers=self.session_config.headers,
                raise_for_status=True,
                timeout=self.session_config.timeout,
            )

        try:
            response = await _request()
        except (ClientConnectionError, TimeoutError) as err:
            raise ServiceUnavailableError from err
        except ClientResponseError as exc:
            if exc.status == 401:
                if self.session_config.refresh_token is None:
                    raise TokenNotRenewableError(NOT_RENEWABLE_MESSAGE) from exc
                if self.session_config.auto_refresh:
                    self.logger.debug("Auto refreshing tokens.")
                    await self.refresh()
                    response = await self._retry(_request, f"API DELETE call to {endpoint} failed.")
                else:
                    raise AccessTokenExpiredError from exc
            elif exc.status == 404:
                raise NotFoundError from exc
            else:
                raise ApiError(f"API DELETE call to {endpoint} failed.") from exc
        return await _json_body(response)

    async def refresh(self) -> None:
        """Refresh tokens."""
        await self.session_config.refresh()

    async def logout(self) -> None:
        """Logout client."""
        try:
            if self.session_config.refresh_token is not None:
                # v2.26 and above
                await self.session_config.session.post(
                    self.session_config.url_for("logout"),
                    ssl=self.session_config.verify_ssl,
                    headers=self.session_config.headers_refresh_logout,
                    cookies=self.session_config.cookies_refresh_logout,
                    raise_for_status=True,
                    timeout=LOGOUT_TIMEOUT,
                )
            else:
                await self._post("logout")
        except (ClientConnectionError, TimeoutError) as err:
            raise ServiceUnavailableError from err
        except ClientResponseError as err:
            raise ApiError("Logout failed.") from err
