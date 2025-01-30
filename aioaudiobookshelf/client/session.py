"""Session configuration."""

from dataclasses import dataclass

from aiohttp import ClientSession


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
