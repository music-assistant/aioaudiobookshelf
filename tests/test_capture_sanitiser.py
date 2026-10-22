"""The capture script must not be able to write a secret into a fixture."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "capture_fixtures.py"
_spec = importlib.util.spec_from_file_location("capture_fixtures", SCRIPT)
assert _spec is not None
assert _spec.loader is not None
capture = importlib.util.module_from_spec(_spec)
# dataclasses resolve their module through sys.modules, so register it first
sys.modules[_spec.name] = capture
_spec.loader.exec_module(capture)

SERVER = "http://abs.local:13378"
JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxIn0.c2lnbmF0dXJl"


def _clean(payload: Any) -> Any:
    return capture.sanitise(payload, server_url=SERVER)


def test_tokens_are_removed() -> None:
    """Abs hands out tokens in the login answer and in the user object."""
    cleaned = _clean({"user": {"id": "1", "token": JWT, "accessToken": JWT, "refreshToken": JWT}})

    assert cleaned["user"]["id"] == "1"
    assert JWT not in str(cleaned)


def test_a_token_hidden_in_a_url_is_removed() -> None:
    """Abs puts a token into the cover and stream urls, see its provider item 8."""
    cleaned = _clean({"url": f"{SERVER}/api/items/li_1/cover?token={JWT}"})

    assert cleaned["url"].startswith("https://abs.example.com/api/items/li_1/cover")
    assert JWT not in cleaned["url"]


def test_paths_and_names_are_replaced() -> None:
    """A fixture must not carry the server's filesystem or who uses it."""
    cleaned = _clean(
        {"path": "/srv/media/books/Some Book", "username": "fabian", "email": "me@example.org"}
    )

    assert cleaned["path"] == "/audiobooks/Some Book"
    assert cleaned["username"] == "listener"
    assert cleaned["email"] == "listener@example.com"


def test_the_server_url_is_replaced_everywhere() -> None:
    """The instance a fixture came from is nobody's business."""
    cleaned = _clean({"items": [{"url": f"{SERVER}/api/items/li_1/play"}]})

    assert cleaned["items"][0]["url"] == "https://abs.example.com/api/items/li_1/play"


def test_an_unclassified_secret_aborts_the_run() -> None:
    """Whatever the key is called, a token shape must stop the whole capture."""
    with pytest.raises(capture.SecretLeakError):
        capture.assert_clean({"something": {"we": [f"Bearer {JWT}"]}})


def test_ids_survive() -> None:
    """Abs' ids look random but are not secret, and a fixture is useless without them."""
    payload = {"id": "li_8p3kf92mdl2k", "libraryId": "lib_3k2mfl", "ino": "123456789"}

    assert _clean(payload) == payload


def test_lists_are_trimmed_but_shapes_kept() -> None:
    """A fixture needs one or two entries, not a whole library."""
    trimmed = capture.trim({"results": [{"id": str(index)} for index in range(10)]})

    assert trimmed == {"results": [{"id": "0"}, {"id": "1"}]}
