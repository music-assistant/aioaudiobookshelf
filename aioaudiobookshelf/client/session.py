"""Calls to /api/session."""

from aioaudiobookshelf.client._base import BaseClient
from aioaudiobookshelf.exceptions import (
    ApiError,
    NotFoundError,
    SessionNotFoundError,
    SessionSyncError,
)
from aioaudiobookshelf.schema.calls_session import (
    CloseOpenSessionsParameters,
    SyncOpenSessionParameters,
)
from aioaudiobookshelf.schema.session import PlaybackSession, PlaybackSessionExpanded


class SessionClient(BaseClient):
    """SessionClient."""

    # get_all_session # admin
    # delete session

    async def sync_local_sessions(self, *, playback_sessions: list[PlaybackSession]) -> None:
        """Sync/ create a local session."""
        try:
            await self._post(
                "/api/session/local-all",
                data={
                    "sessions": [
                        playback_session.to_dict() for playback_session in playback_sessions
                    ]
                },
            )
        except ApiError as err:
            raise SessionSyncError from err

    async def sync_local_session(self, *, playback_session: PlaybackSession) -> None:
        """Sync/ create a local session."""
        try:
            await self._post("/api/session/local", data=playback_session.to_dict())
        except ApiError as err:
            raise SessionSyncError from err

    async def get_open_session(self, *, session_id: str) -> PlaybackSessionExpanded:
        """Get open session."""
        try:
            response = await self._get(f"/api/session/{session_id}")
        except NotFoundError as exc:
            raise SessionNotFoundError from exc
        psession = PlaybackSessionExpanded.from_json(response)
        self.logger.debug(
            "Got playback session %s for %s named %s.",
            psession.id_,
            psession.media_type,
            psession.display_title,
        )
        return psession

    async def sync_open_session(
        self, *, session_id: str, parameters: SyncOpenSessionParameters
    ) -> None:
        """Sync an open session."""
        try:
            await self._post(f"/api/session/{session_id}/sync", data=parameters.to_dict())
        except (ApiError, NotFoundError) as err:
            raise SessionSyncError from err

    async def close_open_session(
        self, *, session_id: str, parameters: CloseOpenSessionsParameters | None = None
    ) -> None:
        """Close open session."""
        _parameters = {} if parameters is None else parameters.to_dict()
        self.logger.debug("Closing playback session %s.", session_id)
        try:
            await self._post(f"/api/session/{session_id}/close", data=_parameters)
        except ApiError as err:
            raise SessionNotFoundError from err
