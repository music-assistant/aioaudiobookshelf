"""Nothing may decode past the wrapping the schema base does."""

import ast
from pathlib import Path

import aioaudiobookshelf

PACKAGE = Path(aioaudiobookshelf.__file__).parent

# mashumaro generates from_dict onto every model, where it raises its own errors
# instead of ours. _BaseModel.from_payload is the one place allowed to call it.
ALLOWED = PACKAGE / "schema" / "__init__.py"


def _calls_from_dict(path: Path) -> list[int]:
    tree = ast.parse(path.read_text())
    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and node.attr == "from_dict"
    ]


def test_from_dict_is_only_called_where_it_is_wrapped() -> None:
    """A model decoded with from_dict raises a mashumaro error, which no caller catches."""
    found = {
        str(path.relative_to(PACKAGE)): lines
        for path in sorted(PACKAGE.rglob("*.py"))
        if path != ALLOWED and (lines := _calls_from_dict(path))
    }

    assert not found, f"use from_payload instead: {found}"
