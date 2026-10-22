"""Every schema model has to report what abs sent as an error of ours."""

import importlib
import inspect
import pkgutil
from dataclasses import is_dataclass

import pytest
from mashumaro.mixins.json import DataClassJSONMixin

import aioaudiobookshelf.schema
from aioaudiobookshelf.exceptions import SchemaError


def _models() -> list[type[DataClassJSONMixin]]:
    """Every decodable model the schema package defines."""
    models = []
    for module in pkgutil.walk_packages(
        aioaudiobookshelf.schema.__path__, f"{aioaudiobookshelf.schema.__name__}."
    ):
        for _, obj in inspect.getmembers(importlib.import_module(module.name)):
            if (
                inspect.isclass(obj)
                and is_dataclass(obj)
                and issubclass(obj, DataClassJSONMixin)
                and obj not in models
            ):
                models.append(obj)
    return models


@pytest.mark.parametrize("model", _models(), ids=lambda model: model.__name__)
def test_a_payload_abs_cannot_have_sent_raises_a_schema_error(
    model: type[DataClassJSONMixin],
) -> None:
    """A model which does not go through the shared base would raise a json error instead."""
    with pytest.raises(SchemaError):
        model.from_json(b"")
