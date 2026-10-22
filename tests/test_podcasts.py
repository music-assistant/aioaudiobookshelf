"""Tests for decoding podcast payloads."""

import json
from typing import Any

from aioaudiobookshelf.schema.library import LibraryItemExpandedPodcast

_FILE_METADATA = {
    "filename": "episode1.mp3",
    "ext": ".mp3",
    "path": "/podcasts/show1/episode1.mp3",
    "relPath": "episode1.mp3",
    "size": 1000,
    "mtimeMs": 1700000000000,
    "ctimeMs": 1700000000000,
    "birthtimeMs": 0,
}


def _episode() -> dict[str, Any]:
    """Build an episode as abs sends it for a file scanned in before abs v2.21.0."""
    audio_file = {
        "index": None,
        "ino": "2",
        "metadata": _FILE_METADATA,
        "addedAt": 1700000000000,
        "updatedAt": 1700000000000,
        "manuallyVerified": False,
        "exclude": False,
        "error": None,
        "format": "MP2/3 (MPEG audio layer 2/3)",
        "duration": 60.0,
        "bitRate": 128000,
        "codec": "mp3",
        "channels": 2,
        "channelLayout": "stereo",
        "mimeType": "audio/mpeg",
    }
    return {
        "libraryItemId": "item1",
        "podcastId": "podcast1",
        "id": "episode1",
        "index": None,
        "title": "Episode 1",
        "chapters": [],
        "addedAt": 1700000000000,
        "updatedAt": 1700000000000,
        "audioFile": audio_file,
        "audioTrack": {
            "index": None,
            "startOffset": 0,
            "duration": 60.0,
            "title": "episode1.mp3",
            "contentUrl": "/api/items/item1/file/2",
            "mimeType": "audio/mpeg",
            "metadata": _FILE_METADATA,
        },
        "duration": 60.0,
        "size": 1000,
    }


def _podcast_item(episode: dict[str, Any]) -> bytes:
    item = {
        "id": "item1",
        "ino": "1",
        "libraryId": "library1",
        "folderId": "folder1",
        "path": "/podcasts/show1",
        "relPath": "show1",
        "isFile": False,
        "addedAt": 1700000000000,
        "updatedAt": 1700000000000,
        "isMissing": False,
        "isInvalid": False,
        "mediaType": "podcast",
        "libraryFiles": [],
        "size": 1000,
        "media": {
            "id": "podcast1",
            "libraryItemId": "item1",
            "autoDownloadEpisodes": False,
            "maxEpisodesToKeep": 0,
            "maxNewEpisodesToDownload": 3,
            "tags": [],
            "size": 1000,
            "metadata": {"title": "Show 1", "genres": [], "explicit": False},
            "episodes": [episode],
        },
    }
    return json.dumps(item).encode()


def test_an_episode_scanned_before_abs_2_21_has_no_audio_file_index() -> None:
    """Abs never backfilled the null index of older scans, see support#6842."""
    item = LibraryItemExpandedPodcast.from_json(_podcast_item(_episode()))

    audio_file = item.media.episodes[0].audio_file
    assert audio_file is not None
    assert audio_file.index is None


def test_an_episode_abs_before_2_7_1_could_not_probe_has_a_duration_of_0() -> None:
    """Abs sent the audio file's null duration, newer ones send 0 instead."""
    episode = _episode()
    episode["audioFile"]["duration"] = None
    episode["audioTrack"]["duration"] = None
    episode["duration"] = None

    item = LibraryItemExpandedPodcast.from_json(_podcast_item(episode))

    assert item.media.episodes[0].duration == 0


def test_an_episode_abs_before_2_18_got_without_a_title_has_an_empty_one() -> None:
    """Abs stored null for a feed item without title, newer ones store an empty one."""
    episode = _episode()
    episode["title"] = None

    item = LibraryItemExpandedPodcast.from_json(_podcast_item(episode))

    assert item.media.episodes[0].title == ""
