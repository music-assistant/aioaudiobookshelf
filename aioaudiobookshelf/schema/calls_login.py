"""Requests and responses to talk to abs api."""

from dataclasses import dataclass
from typing import Annotated

from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.types import Alias

from .server import ServerSettings
from .user import User


@dataclass(kw_only=True)
class LoginParameters(DataClassJSONMixin):
    """Login params."""

    username: str
    password: str


@dataclass(kw_only=True)
class LoginResponse(DataClassJSONMixin):
    """Response to login request."""

    user: User
    user_default_library_id: Annotated[str, Alias("userDefaultLibraryId")]
    server_settings: Annotated[ServerSettings, Alias("serverSettings")]
    source: Annotated[str, Alias("Source")]


# api/authorize, if token is used for authorization
AuthorizeResponse = LoginResponse

# auth/refresh, new in v2.26
RefreshResponse = LoginResponse
