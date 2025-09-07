"""Clients for Audiobookshelf."""

import logging
from collections.abc import Callable
from typing import Any

import socketio
import socketio.exceptions

from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import (
    BadUserError,
    RefreshTokenExpiredError,
    ServiceUnavailableError,
    TokenIsMissingError,
)
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

    def __init__(
        self,
        session_config: SessionConfiguration,
    ) -> None:
        """Init SocketClient."""
        self.session_config = session_config

        self.client = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=0,
            handle_sigint=False,
            ssl_verify=self.session_config.verify_ssl,
        )

        if self.session_config.logger is None:
            self.logger = logging.getLogger(__name__)
            logging.basicConfig()
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger = self.session_config.logger

        self.set_item_callbacks()
        self.set_user_callbacks()
        self.set_podcast_episode_download_callbacks()
        self.set_refresh_token_expired_callback()

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

    def set_refresh_token_expired_callback(
        self, *, on_refresh_token_expired: Callable[[], Any] | None = None
    ) -> None:
        """Set refresh token expired callback."""
        self.on_refresh_token_expired = on_refresh_token_expired

    async def init_client(self) -> None:
        """Initialize the client."""
        self.client.on("connect", handler=self._on_connect)
        self.client.on("connect_error", handler=self._on_connect_error)

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
        """V2.26 and above: access token or api token."""
        if self.session_config.access_token is not None:
            token = self.session_config.access_token
        else:
            if self.session_config.token is None:
                raise TokenIsMissingError
            token = self.session_config.token
        await self.client.emit(event="auth", data=token)
        self.logger.debug("Socket connected.")

    async def _on_connect_error(self, *_: Any) -> None:
        if not self.session_config.auto_refresh or self.session_config.access_token is None:
            return
        # try to refresh token
        self.logger.debug("Auto refreshing token")
        try:
            await self.session_config.refresh()
        except RefreshTokenExpiredError:
            if self.on_refresh_token_expired is not None:
                await self.on_refresh_token_expired()
            return
        except ServiceUnavailableError:
            # socketio will continue trying to reconnect.
            return

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
