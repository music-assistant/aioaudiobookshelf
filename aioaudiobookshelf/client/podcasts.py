"""Calls to /api/podcasts."""

from aioaudiobookshelf.client._base import BaseClient
from aioaudiobookshelf.schema.podcast import PodcastEpisode


class PodcastsClient(BaseClient):
    """PodcastClient."""

    # create podcast
    # get podcast feed
    # feed from opml
    # check for new episodes
    # get podcast episode downloads
    # search podcast feed
    # download podcast episodes
    # match podcast episode

    async def get_podcast_episode(self, *, podcast_id: str, episode_id: str) -> PodcastEpisode:
        """Get podcast episode."""
        data = await self._get(f"/api/podcasts/{podcast_id}/episode/{episode_id}")
        return PodcastEpisode.from_json(data)
