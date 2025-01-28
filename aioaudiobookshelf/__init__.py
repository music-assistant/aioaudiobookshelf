"""Client library for Audiobookshelf."""

from aiohttp.client_exceptions import ClientResponseError

from .client import SessionConfiguration, UserClient
from .exceptions import LoginError
from .schema.requests import LoginRequest, LoginResponse


async def get_user_client(
    *,
    session_config: SessionConfiguration,
    username: str,
    password: str,
) -> UserClient:
    """Get a user client."""
    login_request = LoginRequest(username=username, password=password).to_dict()

    try:
        resp = await session_config.session.post(
            f"{session_config.url}/login",
            json=login_request,
            ssl=session_config.verify_ssl,
            raise_for_status=True,
        )
    except ClientResponseError as exc:
        raise LoginError from exc
    login_response = LoginResponse.from_json(await resp.read())

    return UserClient(session_config=session_config, login_response=login_response)
