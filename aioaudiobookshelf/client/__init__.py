"""Clients for Audiobookshelf."""

import logging
from collections.abc import Callable, Coroutine
from typing import Any
from urllib.parse import urlparse

import socketio
import socketio.exceptions

from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import (
    AbsError,
    BadUserError,
    RefreshTokenExpiredError,
    TokenIsMissingError,
)
from aioaudiobookshelf.schema.author import Author, AuthorExpanded
from aioaudiobookshelf.schema.events_socket import (
    AuthorRemoved,
    LibraryItemRemoved,
    PodcastEpisodeAdded,
    PodcastEpisodeDownload,
    StreamError,
    StreamReset,
    UserItemProgressUpdatedEvent,
)
from aioaudiobookshelf.schema.library import Library, LibraryItemExpanded
from aioaudiobookshelf.schema.media_progress import MediaProgress
from aioaudiobookshelf.schema.playlist import PlaylistExpanded
from aioaudiobookshelf.schema.streams import Stream, StreamProgress
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

EventHandler = Callable[..., Coroutine[Any, Any, None]]


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

        # configuring logging is the caller's business, not a library's
        self.logger = self.session_config.logger or logging.getLogger(__name__)

        self.set_item_callbacks()
        self.set_user_callbacks()
        self.set_library_callbacks()
        self.set_episode_callbacks()
        self.set_podcast_episode_download_callbacks()
        self.set_refresh_token_expired_callback()
        self.set_stream_callbacks()
        self.set_playlist_callbacks()
        self.set_author_callbacks()

        self._auth_retried = False

    def set_item_callbacks(
        self,
        *,
        on_item_added: Callable[[LibraryItemExpanded], Coroutine[Any, Any, None]] | None = None,
        on_item_updated: Callable[[LibraryItemExpanded], Coroutine[Any, Any, None]] | None = None,
        on_item_removed: Callable[[LibraryItemRemoved], Coroutine[Any, Any, None]] | None = None,
        on_items_added: Callable[[list[LibraryItemExpanded]], Coroutine[Any, Any, None]]
        | None = None,
        on_items_updated: Callable[[list[LibraryItemExpanded]], Coroutine[Any, Any, None]]
        | None = None,
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
        on_user_updated: Callable[[User], Coroutine[Any, Any, None]] | None = None,
        on_user_item_progress_updated: Callable[[str, MediaProgress], Coroutine[Any, Any, None]]
        | None = None,
        on_user_session_closed: Callable[[str], Coroutine[Any, Any, None]] | None = None,
    ) -> None:
        """Set user callbacks. on_user_session_closed receives the session's id."""
        self.on_user_updated = on_user_updated
        self.on_user_item_progress_updated = on_user_item_progress_updated
        self.on_user_session_closed = on_user_session_closed

    def set_library_callbacks(
        self,
        *,
        on_library_added: Callable[[Library], Coroutine[Any, Any, None]] | None = None,
        on_library_updated: Callable[[Library], Coroutine[Any, Any, None]] | None = None,
        on_library_removed: Callable[[Library], Coroutine[Any, Any, None]] | None = None,
    ) -> None:
        """Set library callbacks. Abs only sends these to users who may see the library."""
        self.on_library_added = on_library_added
        self.on_library_updated = on_library_updated
        self.on_library_removed = on_library_removed

    def set_episode_callbacks(
        self,
        *,
        on_episode_added: Callable[[PodcastEpisodeAdded], Coroutine[Any, Any, None]] | None = None,
    ) -> None:
        """Set podcast episode callbacks."""
        self.on_episode_added = on_episode_added

    def set_podcast_episode_download_callbacks(
        self,
        *,
        on_episode_download_finished: Callable[[PodcastEpisodeDownload], Coroutine[Any, Any, None]]
        | None = None,
    ) -> None:
        """Set podcast episode download callbacks."""
        self.on_episode_download_finished = on_episode_download_finished

    def set_refresh_token_expired_callback(
        self, *, on_refresh_token_expired: Callable[[], Coroutine[Any, Any, None]] | None = None
    ) -> None:
        """Set refresh token expired callback."""
        self.on_refresh_token_expired = on_refresh_token_expired

    def set_stream_callbacks(
        self,
        *,
        on_stream_open: Callable[[Stream], Coroutine[Any, Any, None]] | None = None,
        on_stream_closed: Callable[[str], Coroutine[Any, Any, None]] | None = None,
        on_stream_progress: Callable[[StreamProgress], Coroutine[Any, Any, None]] | None = None,
        on_stream_ready: Callable[[], Coroutine[Any, Any, None]] | None = None,
        on_stream_reset: Callable[[StreamReset], Coroutine[Any, Any, None]] | None = None,
        on_stream_error: Callable[[StreamError], Coroutine[Any, Any, None]] | None = None,
    ) -> None:
        """Set stream callback."""
        self.on_stream_open = on_stream_open
        self.on_stream_closed = on_stream_closed
        self.on_stream_progress = on_stream_progress
        self.on_stream_ready = on_stream_ready
        self.on_stream_reset = on_stream_reset
        self.on_stream_error = on_stream_error

    def set_playlist_callbacks(
        self,
        *,
        on_playlist_added: Callable[[PlaylistExpanded], Coroutine[Any, Any, None]] | None = None,
        on_playlist_updated: Callable[[PlaylistExpanded], Coroutine[Any, Any, None]] | None = None,
        on_playlist_removed: Callable[[PlaylistExpanded], Coroutine[Any, Any, None]] | None = None,
    ) -> None:
        """Set playlist callbacks."""
        self.on_playlist_added = on_playlist_added
        self.on_playlist_updated = on_playlist_updated
        self.on_playlist_removed = on_playlist_removed

    def set_author_callbacks(
        self,
        *,
        on_author_added: Callable[[Author], Coroutine[Any, Any, None]] | None = None,
        on_author_updated: Callable[[AuthorExpanded], Coroutine[Any, Any, None]] | None = None,
        on_author_removed: Callable[[AuthorRemoved], Coroutine[Any, Any, None]] | None = None,
    ) -> None:
        """Set author callbacks."""
        self.on_author_added = on_author_added
        self.on_author_updated = on_author_updated
        self.on_author_removed = on_author_removed

    async def init_client(self) -> None:
        """Initialize the client."""
        self.client.on("connect", handler=self._on_connect)
        self.client.on("connect_error", handler=self._on_connect_error)
        self.client.on("auth_failed", handler=self._on_auth_failed)
        self.client.on("init", handler=self._on_init)

        self._on_event("user_updated", self._on_user_updated)
        self._on_event("user_item_progress_updated", self._on_user_item_progress_updated)
        self._on_event("user_session_closed", self._on_user_session_closed)

        self._on_event("item_added", self._on_item_added)
        self._on_event("item_updated", self._on_item_updated)
        self._on_event("item_removed", self._on_item_removed)
        self._on_event("items_added", self._on_items_added)
        self._on_event("items_updated", self._on_items_updated)

        self._on_event("episode_added", self._on_episode_added)
        self._on_event("episode_download_finished", self._on_episode_download_finished)

        self._on_event("library_added", self._on_library_added)
        self._on_event("library_updated", self._on_library_updated)
        self._on_event("library_removed", self._on_library_removed)

        self._on_event("stream_open", self._on_stream_open)
        self._on_event("stream_closed", self._on_stream_closed)
        self._on_event("stream_progress", self._on_stream_progress)
        self._on_event("stream_ready", self._on_stream_ready)
        self._on_event("stream_reset", self._on_stream_reset)
        self._on_event("stream_error", self._on_stream_error)

        self._on_event("playlist_added", self._on_playlist_added)
        self._on_event("playlist_updated", self._on_playlist_updated)
        self._on_event("playlist_removed", self._on_playlist_removed)

        self._on_event("author_added", self._on_author_added)
        self._on_event("author_updated", self._on_author_updated)
        self._on_event("author_removed", self._on_author_removed)

        # engineio builds its url from the host alone, so a base path has to be
        # passed separately. abs serves a socket for it, see its SocketAuthority.js
        base_path = urlparse(self.session_config.url).path
        await self.client.connect(
            url=self.session_config.url, socketio_path=f"{base_path}/socket.io"
        )

    def _on_event(self, event: str, handler: EventHandler) -> None:
        """Register a data handler, with the guard socketio does not give it."""

        async def guarded(*args: Any) -> None:
            try:
                await handler(*args)
            except AbsError:
                # socketio runs handlers in their own task and drops what they raise
                self.logger.exception("Could not handle the socket event %s.", event)

        self.client.on(event, handler=guarded)

    async def shutdown(self) -> None:
        """Shutdown client (disconnect, or stop reconnect attempt)."""
        await self.client.shutdown()

    logout = shutdown

    async def _on_connect(self) -> None:
        self._auth_retried = False
        try:
            await self._authenticate()
        except (AbsError, socketio.exceptions.SocketIOError):
            # socketio drops what a handler raises, so this would go unnoticed
            self.logger.exception("Could not authenticate the socket connection.")
            return
        self.logger.debug("Socket connected.")

    async def _authenticate(self) -> None:
        """V2.26 and above: access token or api token."""
        if self.session_config.access_token is not None:
            token = self.session_config.access_token
        else:
            if self.session_config.token is None:
                raise TokenIsMissingError
            token = self.session_config.token
        await self.client.emit(event="auth", data=token)

    async def _on_init(self, *_: Any) -> None:
        # abs sends init once the socket is authenticated
        self._auth_retried = False

    async def _on_auth_failed(self, *_: Any) -> None:
        # socketio runs handlers in their own task, so errors would go unnoticed
        try:
            await self._handle_auth_failed()
        except (AbsError, socketio.exceptions.SocketIOError):
            self.logger.exception("Could not handle a rejected socket authentication.")

    async def _handle_auth_failed(self) -> None:
        # abs rejects e.g. an expired access token here, the connection itself stays up
        if self.session_config.access_token is None:
            # a rejected api key or pre v2.26 token cannot be refreshed
            self.logger.warning(
                "Socket authentication failed, live updates are unavailable. "
                "Audiobookshelf accepts only access tokens for socket connections."
            )
            await self.client.disconnect()
            return
        # not awaiting between test and set keeps concurrent events to one retry
        if self._auth_retried or not self.session_config.auto_refresh:
            self.logger.warning("Socket authentication failed, live updates are unavailable.")
            return
        self._auth_retried = True
        self.logger.debug("Socket authentication failed, refreshing token.")
        try:
            await self.session_config.refresh()
        except RefreshTokenExpiredError:
            await self._notify_refresh_token_expired()
        except AbsError:
            return
        await self._authenticate()

    async def _notify_refresh_token_expired(self) -> None:
        if self.on_refresh_token_expired is None:
            return
        try:
            await self.on_refresh_token_expired()
        except Exception:
            # the callback belongs to the caller, so anything can come out of it
            self.logger.exception("The refresh token expired callback failed.")

    async def _on_connect_error(self, *_: Any) -> None:
        # abs rejects a token with auth_failed, never here, so there is nothing to renew:
        # the server was not reachable, and socketio keeps reconnecting on its own
        self.logger.debug("Socket could not connect, socketio will retry.")

    async def _on_user_updated(self, data: dict[str, Any]) -> None:
        if self.on_user_updated is not None:
            await self.on_user_updated(User.from_payload(data))

    async def _on_user_item_progress_updated(self, data: dict[str, Any]) -> None:
        if self.on_user_item_progress_updated is not None:
            event = UserItemProgressUpdatedEvent.from_payload(data)
            await self.on_user_item_progress_updated(event.id_, event.data)

    async def _on_user_session_closed(self, session_id: str) -> None:
        # abs closes a session on a restart, and 36h after its last update,
        # see its managers/PlaybackSessionManager.js
        if self.on_user_session_closed is not None:
            await self.on_user_session_closed(session_id)

    async def _on_item_added(self, data: dict[str, Any]) -> None:
        if self.on_item_added is not None:
            await self.on_item_added(LibraryItemExpanded.from_payload(data))

    async def _on_item_updated(self, data: dict[str, Any]) -> None:
        if self.on_item_updated is not None:
            await self.on_item_updated(LibraryItemExpanded.from_payload(data))

    async def _on_item_removed(self, data: dict[str, Any]) -> None:
        if self.on_item_removed is not None:
            await self.on_item_removed(LibraryItemRemoved.from_payload(data))

    async def _on_items_added(self, data: list[dict[str, Any]]) -> None:
        if self.on_items_added is not None:
            await self.on_items_added([LibraryItemExpanded.from_payload(x) for x in data])

    async def _on_items_updated(self, data: list[dict[str, Any]]) -> None:
        if self.on_items_updated is not None:
            await self.on_items_updated([LibraryItemExpanded.from_payload(x) for x in data])

    async def _on_episode_added(self, data: dict[str, Any]) -> None:
        if self.on_episode_added is not None:
            await self.on_episode_added(PodcastEpisodeAdded.from_payload(data))

    async def _on_library_added(self, data: dict[str, Any]) -> None:
        if self.on_library_added is not None:
            await self.on_library_added(Library.from_payload(data))

    async def _on_library_updated(self, data: dict[str, Any]) -> None:
        if self.on_library_updated is not None:
            await self.on_library_updated(Library.from_payload(data))

    async def _on_library_removed(self, data: dict[str, Any]) -> None:
        if self.on_library_removed is not None:
            await self.on_library_removed(Library.from_payload(data))

    async def _on_episode_download_finished(self, data: dict[str, Any]) -> None:
        if self.on_episode_download_finished is not None:
            await self.on_episode_download_finished(PodcastEpisodeDownload.from_payload(data))

    async def _on_stream_open(self, data: dict[str, Any]) -> None:
        if self.on_stream_open is not None:
            await self.on_stream_open(Stream.from_payload(data))

    async def _on_stream_closed(self, stream_id: str) -> None:
        if self.on_stream_closed is not None:
            await self.on_stream_closed(stream_id)

    async def _on_stream_progress(self, data: dict[str, Any]) -> None:
        if self.on_stream_progress is not None:
            await self.on_stream_progress(StreamProgress.from_payload(data))

    async def _on_stream_ready(self) -> None:
        if self.on_stream_ready is not None:
            await self.on_stream_ready()

    async def _on_stream_reset(self, data: dict[str, Any]) -> None:
        if self.on_stream_reset is not None:
            await self.on_stream_reset(StreamReset.from_payload(data))

    async def _on_stream_error(self, data: dict[str, Any]) -> None:
        if self.on_stream_error is not None:
            await self.on_stream_error(StreamError.from_payload(data))

    async def _on_playlist_added(self, data: dict[str, Any]) -> None:
        if self.on_playlist_added is not None:
            await self.on_playlist_added(PlaylistExpanded.from_payload(data))

    async def _on_playlist_updated(self, data: dict[str, Any]) -> None:
        if self.on_playlist_updated is not None:
            await self.on_playlist_updated(PlaylistExpanded.from_payload(data))

    async def _on_playlist_removed(self, data: dict[str, Any]) -> None:
        if self.on_playlist_removed is not None:
            await self.on_playlist_removed(PlaylistExpanded.from_payload(data))

    async def _on_author_added(self, data: dict[str, Any]) -> None:
        if self.on_author_added is not None:
            await self.on_author_added(Author.from_payload(data))

    async def _on_author_updated(self, data: dict[str, Any]) -> None:
        if self.on_author_updated is not None:
            await self.on_author_updated(AuthorExpanded.from_payload(data))

    async def _on_author_removed(self, data: dict[str, Any]) -> None:
        if self.on_author_removed is not None:
            await self.on_author_removed(AuthorRemoved.from_payload(data))
