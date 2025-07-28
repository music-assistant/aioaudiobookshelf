"""Session Configuration."""

import logging
from dataclasses import dataclass

from aiohttp.client import ClientSession

from aioaudiobookshelf.exceptions import TokenIsMissingError


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
