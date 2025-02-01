"""Server Schema."""

from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import Annotated

from mashumaro.types import Alias

from . import _BaseModel


class ServerSettingsMetadataFileFormat(StrEnum):
    """ServerSettingsMetadataFileFormat."""

    ABS = "abs"
    JSON = "json"


class ServerSettingsDateFormat(StrEnum):
    """ServerSettingsDateFormat."""

    MM_DD_YYYY = "MM/dd/yyyy"
    DD_MM_YYYY = "dd/MM/yyyy"
    DDpMMpYYYY = "dd.MM.yyyy"
    YYYY_MM_DD = "yyyy-MM-dd"
    MMM_DO_YYYY = "MMM do, yyyy"
    MMMM_DO_YYYY = "MMMM do, yyyy"
    DD_MMM_YYYY = "dd MMM yyyy"
    DD_MMMM_YYYY = "dd MMMM yyyy"


class ServerSettingsTimeFormat(StrEnum):
    """ServerSettingsTimeFormat."""

    TWENTY_FOUR_HOOUR = "HH:mm"
    TWELVE_HOUR = "h:mma"


class ServerLogLevel(Enum):
    """ServerLogLevel."""

    DEBUG = 1
    INFO = 2
    WARNING = 3


@dataclass(kw_only=True)
class ServerSettings(_BaseModel):
    """ServerSettings."""

    id: Annotated[str, Alias("id")]
    scanner_find_covers: Annotated[bool, Alias("scannerFindCovers")]
    scanner_cover_provider: Annotated[str, Alias("scannerCoverProvider")]
    scanner_parse_subtitle: Annotated[bool, Alias("scannerParseSubtitle")]
    scanner_prefer_matched_metadata: Annotated[bool, Alias("scannerPreferMatchedMetadata")]
    scanner_disable_watcher: Annotated[bool, Alias("scannerDisableWatcher")]
    store_cover_with_item: Annotated[bool, Alias("storeCoverWithItem")]
    store_metadata_with_item: Annotated[bool, Alias("storeMetadataWithItem")]
    metadata_file_format: Annotated[ServerSettingsMetadataFileFormat, Alias("metadataFileFormat")]
    rate_limit_login_requests: Annotated[int, Alias("rateLimitLoginRequests")]
    rate_limit_login_window: Annotated[int, Alias("rateLimitLoginWindow")]  # ms
    backup_schedule: Annotated[str, Alias("backupSchedule")]
    backups_to_keep: Annotated[int, Alias("backupsToKeep")]
    max_backup_size: Annotated[int, Alias("maxBackupSize")]  # GB
    logger_daily_logs_to_keep: Annotated[int, Alias("loggerDailyLogsToKeep")]
    logger_scanner_logs_to_keep: Annotated[int, Alias("loggerScannerLogsToKeep")]
    home_bookshelf_view: Annotated[int, Alias("homeBookshelfView")]
    bookshelf_view: Annotated[int, Alias("bookshelfView")]
    sorting_ignore_prefix: Annotated[bool, Alias("sortingIgnorePrefix")]
    sorting_prefixes: Annotated[list[str], Alias("sortingPrefixes")]
    chromecast_enabled: Annotated[bool, Alias("chromecastEnabled")]
    date_format: Annotated[ServerSettingsDateFormat, Alias("dateFormat")]
    time_format: Annotated[ServerSettingsTimeFormat, Alias("timeFormat")]
    language: str
    log_level: Annotated[ServerLogLevel, Alias("logLevel")]
    version: str
