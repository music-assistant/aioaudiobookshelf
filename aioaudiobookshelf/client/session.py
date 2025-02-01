"""Calls to /api/session."""

from aioaudiobookshelf.client._base import BaseClient
from aioaudiobookshelf.schema.calls_session import CloseOpenSessionsParameters
from aioaudiobookshelf.schema.session import PlaybackSessionExpanded


class SessionClient(BaseClient):
    """SessionClient."""

    # get_all_session # admin
    # delete session
    # sync local session(s)

    async def get_open_session(self, *, session_id: str) -> PlaybackSessionExpanded:
        """Get open session."""
        response = await self._get(f"/api/session/{session_id}")
        psession = PlaybackSessionExpanded.from_json(response)
        self.logger.debug(
            "Got playback session %s for %s named %s.",
            psession.id_,
            psession.media_type,
            psession.display_title,
        )
        return psession

    # sync open session

    async def close_open_session(
        self, *, session_id: str, parameters: CloseOpenSessionsParameters | None = None
    ) -> None:
        """Close open session."""
        _parameters = {} if parameters is None else parameters.to_dict()
        self.logger.debug("Closing playback session %s.", session_id)
        await self._post(f"/api/session/{session_id}/close", data=_parameters)
