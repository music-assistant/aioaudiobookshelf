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
        return PlaybackSessionExpanded.from_json(response)

    # sync open session

    async def close_open_session(
        self, *, session_id: str, parameters: CloseOpenSessionsParameters | None = None
    ) -> None:
        """Close open session."""
        _parameters = {} if parameters is None else parameters.to_dict()
        await self._post(f"/api/session/{session_id}/close", data=_parameters)
