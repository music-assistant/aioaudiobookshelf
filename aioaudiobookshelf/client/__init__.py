"""Clients for Audiobookshelf."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import socketio
import socketio.exceptions
from aiohttp import ClientSession

from aioaudiobookshelf.exceptions import BadUserError, TokenIsMissingError
from aioaudiobookshelf.schema.events_socket import (
    LibraryItemRemoved,
    PodcastEpisodeDownload,
    UserItemProgressUpdatedEvent,
)
from aioaudiobookshelf.schema.library import LibraryItemExpanded
from aioaudiobookshelf.schema.media_progress import MediaProgress
from aioaudiobookshelf.schema.user import User, UserType

from .authors import AuthorsClient
from .collections_ import CollectionsClient
from .items import ItemsClient
from .libraries import LibrariesClient
from .me import MeClient
from .playlists import PlaylistsClient
from .podcasts import PodcastsClient
from .series import SeriesClient
from .session import SessionClient


@dataclass(kw_only=True)
class SessionConfiguration:
    """Session configuration for abs client."""

    session: ClientSession
    url: str
    verify_ssl: bool = True
    token: str | None = None
    pagination_items_per_page: int = 10
    logger: logging.Logger | None = None

    @property
    def headers(self) -> dict[str, str]:
        """Session headers."""
        if self.token is None:
            raise TokenIsMissingError("Token not set.")
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
    SessionClient,
    PodcastsClient,
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


class SocketClient:
    """Client for connecting to abs' socket."""

    def __init__(self, session_config: SessionConfiguration) -> None:
        """Init SocketClient."""
        self.session_config = session_config

        self.client = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=0,
            handle_sigint=False,
            ssl_verify=self.session_config.verify_ssl,
        )

        self.set_item_callbacks()
        self.set_user_callbacks()
        self.set_podcast_episode_download_callbacks()

    def set_item_callbacks(
        self,
        *,
        on_item_added: Callable[[LibraryItemExpanded], Any] | None = None,
        on_item_updated: Callable[[LibraryItemExpanded], Any] | None = None,
        on_item_removed: Callable[[LibraryItemRemoved], Any] | None = None,
        on_items_added: Callable[[list[LibraryItemExpanded]], Any] | None = None,
        on_items_updated: Callable[[list[LibraryItemExpanded]], Any] | None = None,
    ) -> None:
        """Set item callbacks."""
        self.on_item_added = on_item_added
        self.on_item_updated = on_item_updated
        self.on_item_removed = on_item_removed
        self.on_items_added = on_items_added
        self.on_items_updated = on_items_updated

    def set_user_callbacks(
        self,
        *,
        on_user_updated: Callable[[User], Any] | None = None,
        on_user_item_progress_updated: Callable[[str, MediaProgress], Any] | None = None,
    ) -> None:
        """Set user callbacks."""
        self.on_user_updated = on_user_updated
        self.on_user_item_progress_updated = on_user_item_progress_updated

    def set_podcast_episode_download_callbacks(
        self, *, on_episode_download_finished: Callable[[PodcastEpisodeDownload], Any] | None = None
    ) -> None:
        """Set podcast episode download callbacks."""
        self.on_episode_download_finished = on_episode_download_finished

    async def init_client(self) -> None:
        """Initialize the client."""
        self.client.on("connect", handler=self._on_connect)

        self.client.on("user_updated", handler=self._on_user_updated)
        self.client.on("user_item_progress_updated", handler=self._on_user_item_progress_updated)

        self.client.on("item_added", handler=self._on_item_added)
        self.client.on("item_updated", handler=self._on_item_updated)
        self.client.on("item_removed", handler=self._on_item_removed)
        self.client.on("items_added", handler=self._on_items_added)
        self.client.on("items_updated", handler=self._on_items_updated)

        self.client.on("episode_download_finished", handler=self._on_episode_download_finished)

        await self.client.connect(url=self.session_config.url)

    async def shutdown(self) -> None:
        """Shutdown client (disconnect, or stop reconnect attempt)."""
        await self.client.shutdown()

    logout = shutdown

    async def _on_connect(self) -> None:
        await self.client.emit(event="auth", data=self.session_config.token)

    async def _on_user_updated(self, data: dict[str, Any]) -> None:
        if self.on_user_updated is not None:
            await self.on_user_updated(User.from_dict(data))

    async def _on_user_item_progress_updated(self, data: dict[str, Any]) -> None:
        if self.on_user_item_progress_updated is not None:
            event = UserItemProgressUpdatedEvent.from_dict(data)
            await self.on_user_item_progress_updated(event.id_, event.data)

    async def _on_item_added(self, data: dict[str, Any]) -> None:
        if self.on_item_added is not None:
            await self.on_item_added(LibraryItemExpanded.from_dict(data))

    async def _on_item_updated(self, data: dict[str, Any]) -> None:
        if self.on_item_updated is not None:
            await self.on_item_updated(LibraryItemExpanded.from_dict(data))

    async def _on_item_removed(self, data: dict[str, Any]) -> None:
        if self.on_item_removed is not None:
            await self.on_item_removed(LibraryItemRemoved.from_dict(data))

    async def _on_items_added(self, data: list[dict[str, Any]]) -> None:
        if self.on_items_added is not None:
            await self.on_items_added([LibraryItemExpanded.from_dict(x) for x in data])

    async def _on_items_updated(self, data: list[dict[str, Any]]) -> None:
        if self.on_items_updated is not None:
            await self.on_items_updated([LibraryItemExpanded.from_dict(x) for x in data])

    async def _on_episode_download_finished(self, data: dict[str, Any]) -> None:
        if self.on_episode_download_finished is not None:
            await self.on_episode_download_finished(PodcastEpisodeDownload.from_dict(data))
