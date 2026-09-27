"""Tests for passing a library's mark-as-finished settings to a progress update."""

from aioaudiobookshelf.client.me import MeClient

from .helpers import RecordingSession, make_client


async def test_settings_ride_along_with_the_position() -> None:
    """Abs weighs them against the position it is given, so they belong to that call."""
    session = RecordingSession()

    await make_client(MeClient, session).update_my_media_progress(
        item_id="item1",
        duration_seconds=400,
        progress_seconds=100,
        is_finished=False,
        mark_as_finished_time_remaining=60,
        mark_as_finished_percent_complete=95,
    )

    assert session.payloads == [
        {"isFinished": False},
        {"progress": 0.25},
        {
            "duration": 400,
            "currentTime": 100,
            "markAsFinishedTimeRemaining": 60,
            "markAsFinishedPercentComplete": 95,
        },
    ]


async def test_only_the_setting_which_is_given_is_sent() -> None:
    """Abs reads them independently, and a None would not mean the same as absent."""
    session = RecordingSession()

    await make_client(MeClient, session).update_my_media_progress(
        item_id="item1",
        duration_seconds=400,
        progress_seconds=100,
        is_finished=False,
        mark_as_finished_percent_complete=95,
    )

    assert session.payloads[-1] == {
        "duration": 400,
        "currentTime": 100,
        "markAsFinishedPercentComplete": 95,
    }


async def test_without_settings_the_payload_is_unchanged() -> None:
    """A caller which passes none must see exactly what it saw before."""
    session = RecordingSession()

    await make_client(MeClient, session).update_my_media_progress(
        item_id="item1", duration_seconds=400, progress_seconds=100, is_finished=False
    )

    assert session.payloads[-1] == {"duration": 400, "currentTime": 100}


async def test_settings_are_not_sent_with_the_finished_flag() -> None:
    """Abs would weigh them against the stored position, and could re-finish the item."""
    session = RecordingSession()

    await make_client(MeClient, session).update_my_media_progress(
        item_id="item1",
        duration_seconds=400,
        progress_seconds=100,
        is_finished=True,
        mark_as_finished_time_remaining=60,
    )

    assert session.payloads == [{"isFinished": True}]
