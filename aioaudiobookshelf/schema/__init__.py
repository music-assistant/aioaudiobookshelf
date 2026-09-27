"""Schema for Audiobookshelf (abs)."""

import json
from typing import Any, TypeVar

from mashumaro.config import BaseConfig
from mashumaro.mixins.json import DataClassJSONMixin, Decoder, EncodedData

from aioaudiobookshelf.exceptions import SchemaError

T = TypeVar("T", bound="_BaseModel")

# what json and mashumaro raise for a payload they cannot read
DECODE_ERRORS = (ValueError, LookupError)


class _BaseModel(DataClassJSONMixin):
    """Model shared between schema definitions."""

    class Config(BaseConfig):
        """Base configuration."""

        forbid_extra_keys = False
        serialize_by_alias = True

    @classmethod
    def from_json(
        cls: type[T],
        data: EncodedData,
        decoder: Decoder = json.loads,
        **from_dict_kwargs: Any,
    ) -> T:
        """Decode, reporting what abs sent as an error of ours.

        mashumaro generates from_dict on every subclass, so this is the one
        inherited entry point there is; an already parsed payload goes through
        from_payload().
        """
        try:
            return super().from_json(data, decoder, **from_dict_kwargs)
        except DECODE_ERRORS as err:
            raise SchemaError(f"Could not read a {cls.__name__} from abs.") from err

    @classmethod
    def from_payload(cls: type[T], data: dict[str, Any]) -> T:
        """Decode an already parsed payload, e.g. a socket event."""
        try:
            return cls.from_dict(data)
        except DECODE_ERRORS as err:
            raise SchemaError(f"Could not read a {cls.__name__} from abs.") from err
