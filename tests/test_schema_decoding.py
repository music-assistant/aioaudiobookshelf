"""Decoding the payloads abs actually sends."""

from typing import Any

import pytest

from aioaudiobookshelf.schema.audio import AudioTrack
from aioaudiobookshelf.schema.book import BookMetadata
from aioaudiobookshelf.schema.calls_login import LoginResponse
from aioaudiobookshelf.schema.events_socket import AuthorRemoved
from aioaudiobookshelf.schema.library import Library, LibraryIcons, LibraryItemPodcast
from aioaudiobookshelf.schema.podcast import Podcast, PodcastEpisode, PodcastMetadata
from aioaudiobookshelf.schema.server import ServerSettings
from aioaudiobookshelf.schema.session import PlaybackSession

Payload = dict[str, Any]


def _without(payload: Payload, *keys: str) -> Payload:
    return {key: value for key, value in payload.items() if key not in keys}


def _file_metadata() -> Payload:
    return {
        "filename": "episode.mp3",
        "ext": ".mp3",
        "path": "/podcasts/episode.mp3",
        "relPath": "episode.mp3",
        "size": 1,
        "mtimeMs": 1,
        "ctimeMs": 1,
        "birthtimeMs": 1,
    }


def _book_metadata() -> Payload:
    return {
        "title": "A Book",
        "genres": [],
        "explicit": False,
        "authors": [{"id": "author1", "name": "An Author"}],
        "narrators": ["A Narrator"],
        "series": [{"id": "series1", "name": "A Series", "sequence": "1"}],
    }


def _podcast_metadata() -> Payload:
    return {"title": "A Podcast", "genres": [], "explicit": False}


def _session(media_type: str, media_metadata: Payload) -> Payload:
    return {
        "id": "session1",
        "userId": "user1",
        "libraryId": "library1",
        "libraryItemId": "item1",
        "mediaType": media_type,
        "mediaMetadata": media_metadata,
        "displayTitle": "A Title",
        "displayAuthor": None,
        "coverPath": None,
        "duration": 100.0,
        "playMethod": 0,
        "mediaPlayer": "unknown",
        "deviceInfo": {},
        "serverVersion": "2.36.1",
        "date": "2026-09-27",
        "dayOfWeek": "Sunday",
        "timeListening": 1.0,
        "startTime": 0.0,
        "currentTime": 1.0,
        "startedAt": 1,
        "updatedAt": 1,
    }


def _server_settings(*, backup_schedule: str | bool = False) -> Payload:
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
        "backupSchedule": backup_schedule,
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
        "logLevel": 2,
        "version": "2.36.1",
    }


def _user() -> Payload:
    return {
        "id": "user1",
        "username": "someone",
        "type": "user",
        "mediaProgress": [],
        "seriesHideFromContinueListening": [],
        "bookmarks": [],
        "isActive": True,
        "isLocked": False,
        "createdAt": 1,
        "permissions": {
            "download": True,
            "update": False,
            "delete": False,
            "upload": False,
            "accessAllLibraries": True,
            "accessAllTags": True,
            "accessExplicitContent": True,
        },
    }


def _library(icon: str) -> Payload:
    return {
        "id": "library1",
        "name": "A Library",
        "folders": [
            {"id": "folder1", "fullPath": "/podcasts", "libraryId": "library1", "addedAt": 1}
        ],
        "displayOrder": 1,
        "icon": icon,
        "mediaType": "podcast",
        "provider": "audiobookshelf",
        "settings": {},
        "createdAt": 1,
        "lastUpdate": 1,
    }


def _library_item() -> Payload:
    return {
        "id": "item1",
        "ino": "1",
        "libraryId": "library1",
        "folderId": "folder1",
        "path": "/podcasts/a",
        "relPath": "a",
        "isFile": False,
        "mtimeMs": 1,
        "ctimeMs": 1,
        "birthtimeMs": 1,
        "addedAt": 1,
        "updatedAt": 1,
        "isMissing": False,
        "isInvalid": False,
        "libraryFiles": [],
        "mediaType": "podcast",
        "media": {
            "libraryItemId": "item1",
            "metadata": _podcast_metadata(),
            "episodes": [],
            "autoDownloadEpisodes": False,
            "autoDownloadSchedule": "",
            "maxEpisodesToKeep": 0,
            "maxNewEpisodesToDownload": 0,
        },
    }


def test_audio_track_carries_its_mime_type() -> None:
    """Abs sends mimeType, see its objects/files/AudioTrack.js."""
    track = AudioTrack.from_dict(
        {
            "index": 1,
            "startOffset": 0.0,
            "duration": 1.0,
            "title": "A Track",
            "contentUrl": "/content",
            "mimeType": "audio/mpeg",
            "metadata": _file_metadata(),
        }
    )

    assert track.mime_type == "audio/mpeg"


def test_podcast_episode_carries_its_audio_file() -> None:
    """Abs sends audioFile, and its probe-derived fields can be missing."""
    episode = PodcastEpisode.from_dict(
        {
            "libraryItemId": "item1",
            "id": "episode1",
            "season": "",
            "episode": "",
            "episodeType": "",
            "title": "Episode 1",
            "subtitle": "",
            "description": "",
            "pubDate": "",
            "addedAt": 1,
            "updatedAt": 1,
            "audioFile": {
                "index": 1,
                "ino": "2",
                "metadata": _without(_file_metadata(), "ctimeMs"),
                "addedAt": 1,
                "updatedAt": 1,
                "manuallyVerified": False,
                "exclude": False,
                "duration": None,
            },
        }
    )

    assert episode.audio_file is not None
    # everything abs derives from probing the file, which it could not do here
    assert episode.audio_file.codec is None
    assert episode.audio_file.time_base is None
    assert episode.audio_file.format is None
    assert episode.audio_file.metadata.changed_time_ms is None


def test_book_session_keeps_its_book_metadata() -> None:
    """A book session must not decode as a podcast, which drops authors and narrators."""
    session = PlaybackSession.from_dict(_session("book", _book_metadata()))

    assert isinstance(session.media_metadata, BookMetadata)
    assert [author.name for author in session.media_metadata.authors] == ["An Author"]
    assert [series.name for series in session.media_metadata.series] == ["A Series"]
    assert session.media_metadata.narrators == ["A Narrator"]


def test_podcast_session_keeps_its_podcast_metadata() -> None:
    """A podcast session has no authors, so it still has to land on PodcastMetadata."""
    session = PlaybackSession.from_dict(_session("podcast", _podcast_metadata()))

    assert isinstance(session.media_metadata, PodcastMetadata)
    assert session.media_metadata.title == "A Podcast"


def test_session_without_a_cover_or_author() -> None:
    """Abs leaves both empty for an item it knows little about."""
    session = PlaybackSession.from_dict(_session("podcast", _podcast_metadata()))

    assert session.cover_path is None
    assert session.display_author is None


@pytest.mark.parametrize(
    ("icon", "expected"),
    [("database", LibraryIcons.DATABASE), ("an-icon-abs-added-later", LibraryIcons.UNKNOWN)],
)
def test_library_icon_survives_an_unknown_value(icon: str, expected: LibraryIcons) -> None:
    """A new icon in abs must not break a whole library listing."""
    library = Library.from_dict(_library(icon))

    assert library.icon == expected


def test_library_item_without_timestamps() -> None:
    """Abs can leave the file timestamps out, see music-assistant/support#3914."""
    item = LibraryItemPodcast.from_dict(
        _without(_library_item(), "mtimeMs", "ctimeMs", "birthtimeMs")
    )

    assert item.modified_time_ms is None
    assert item.changed_time_ms is None
    assert item.created_time_ms is None


@pytest.mark.parametrize("backup_schedule", [False, "30 1 * * *"])
def test_backup_schedule_keeps_its_type(backup_schedule: str | bool) -> None:
    """Abs sends false when auto backups are off, which must not become the text "False"."""
    settings = ServerSettings.from_dict(_server_settings(backup_schedule=backup_schedule))

    assert settings.backup_schedule == backup_schedule


def test_login_without_a_default_library() -> None:
    """A user without a default library still logs in."""
    response = LoginResponse.from_dict(
        {"user": _user(), "serverSettings": _server_settings(), "Source": "server"}
    )

    assert response.user_default_library_id is None


def test_author_removed_payload() -> None:
    """Abs sends only an id and a library id, see its routers/ApiRouter.js."""
    removed = AuthorRemoved.from_dict({"id": "author1", "libraryId": "library1"})

    assert (removed.id_, removed.library_id) == ("author1", "library1")


def test_podcast_without_a_download_schedule() -> None:
    """Abs nulls the column whenever the payload is not a string, see its models/Podcast.js."""
    podcast = Podcast.from_dict(
        {
            "libraryItemId": "item1",
            "metadata": _podcast_metadata(),
            "episodes": [],
            "autoDownloadEpisodes": False,
            "autoDownloadSchedule": None,
            "maxEpisodesToKeep": 0,
            "maxNewEpisodesToDownload": 0,
        }
    )

    assert podcast.auto_download_schedule is None
