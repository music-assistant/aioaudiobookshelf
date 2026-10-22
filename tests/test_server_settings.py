"""Tests for decoding abs' server settings."""

from aioaudiobookshelf.schema.server import ServerSettings


def test_a_fractional_max_backup_size_is_kept() -> None:
    """Abs' web client sends Number(maxBackupSize), so half a GB stays 0.5."""
    settings = ServerSettings.from_payload(
        {
            "id": "server-settings",
            "scannerParseSubtitle": False,
            "scannerFindCovers": False,
            "scannerCoverProvider": "google",
            "scannerPreferMatchedMetadata": False,
            "scannerDisableWatcher": False,
            "storeCoverWithItem": False,
            "storeMetadataWithItem": False,
            "metadataFileFormat": "json",
            "rateLimitLoginRequests": 10,
            "rateLimitLoginWindow": 600000,
            "allowIframe": False,
            "backupSchedule": False,
            "backupsToKeep": 2,
            "maxBackupSize": 0.5,
            "loggerDailyLogsToKeep": 7,
            "loggerScannerLogsToKeep": 2,
            "homeBookshelfView": 1,
            "bookshelfView": 1,
            "podcastEpisodeSchedule": "0 * * * *",
            "sortingIgnorePrefix": False,
            "sortingPrefixes": ["the", "a"],
            "chromecastEnabled": False,
            "dateFormat": "MM/dd/yyyy",
            "timeFormat": "HH:mm",
            "language": "en-us",
            "allowedOrigins": [],
            "logLevel": 2,
            "version": "2.37.1",
        }
    )

    assert settings.max_backup_size == 0.5
