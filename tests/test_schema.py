"""Tests for schema definitions abs does not always fill."""

from typing import Any

import pytest

from aioaudiobookshelf.schema.podcast import PodcastEpisode
from aioaudiobookshelf.schema.server import ServerLogLevel, ServerSettings


def _scanned_episode() -> dict[str, Any]:
    # an episode abs created from a local file, see its scanner/PodcastScanner.js
    return {
        "libraryItemId": "item1",
        "id": "episode1",
        "index": 1,
        "season": None,
        "episode": None,
        "episodeType": None,
        "title": "Episode 1",
        "subtitle": None,
        "description": None,
        "chapters": [],
        "pubDate": None,
        "publishedAt": None,
        "addedAt": 1,
        "updatedAt": 1,
    }


def _server_settings(log_level: int) -> dict[str, Any]:
    return {
        "id": "server-settings",
        "scannerFindCovers": False,
        "scannerCoverProvider": "google",
        "scannerParseSubtitle": False,
        "scannerPreferMatchedMetadata": False,
        "scannerDisableWatcher": False,
        "storeCoverWithItem": False,
        "storeMetadataWithItem": False,
        "metadataFileFormat": "json",
        "rateLimitLoginRequests": 10,
        "rateLimitLoginWindow": 600000,
        "backupSchedule": "30 1 * * *",
        "backupsToKeep": 2,
        "maxBackupSize": 1,
        "loggerDailyLogsToKeep": 7,
        "loggerScannerLogsToKeep": 2,
        "homeBookshelfView": 1,
        "bookshelfView": 1,
        "sortingIgnorePrefix": False,
        "sortingPrefixes": ["the"],
        "chromecastEnabled": False,
        "dateFormat": "MM/dd/yyyy",
        "timeFormat": "HH:mm",
        "language": "en-us",
        "logLevel": log_level,
        "version": "2.36.1",
    }


@pytest.mark.parametrize(
    "field_name", ["season", "episode", "episode_type", "subtitle", "description", "pub_date"]
)
def test_unset_episode_fields_stay_empty(field_name: str) -> None:
    """A field abs left empty is None, not the string "None"."""
    episode = PodcastEpisode.from_dict(_scanned_episode())

    assert getattr(episode, field_name) is None


def test_enclosure_without_type_and_length() -> None:
    """Abs sends an enclosure without a type or a length."""
    payload = _scanned_episode()
    payload["enclosure"] = {"url": "http://abs.local/feed.mp3", "type": None, "length": None}

    episode = PodcastEpisode.from_dict(payload)

    assert episode.enclosure is not None
    assert episode.enclosure.type_ is None
    assert episode.enclosure.length is None


@pytest.mark.parametrize("log_level", list(range(7)))
def test_every_abs_log_level_decodes(log_level: int) -> None:
    """Abs' log levels run from TRACE to NOTE, and a login must not fail over them."""
    settings = ServerSettings.from_dict(_server_settings(log_level))

    assert settings.log_level == ServerLogLevel(log_level)
