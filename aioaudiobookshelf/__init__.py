"""Client library for Audiobookshelf."""

from aiohttp.client_exceptions import ClientResponseError, InvalidUrlClientError

from aioaudiobookshelf.client import AdminClient, SocketClient, UserClient
from aioaudiobookshelf.client.session_configuration import SessionConfiguration
from aioaudiobookshelf.exceptions import LoginError, TokenIsMissingError
from aioaudiobookshelf.helpers import get_login_response
from aioaudiobookshelf.schema.calls_login import AuthorizeResponse

__version__ = "0.1.8"


async def _get_authorize_response(*, session_config: SessionConfiguration) -> AuthorizeResponse:
    """Login via token."""
    try:
        resp = await session_config.session.post(
            f"{session_config.url}/api/authorize",
            ssl=session_config.verify_ssl,
            raise_for_status=True,
            headers=session_config.headers,
        )
    except (ClientResponseError, InvalidUrlClientError, TokenIsMissingError) as exc:
        raise LoginError from exc
    return AuthorizeResponse.from_json(await resp.read())


async def get_user_client_by_token(*, session_config: SessionConfiguration) -> UserClient:
    """Get user client by token. Token must be set in session_config."""
    authorize_response = await _get_authorize_response(session_config=session_config)
    return UserClient(session_config=session_config, login_response=authorize_response)


async def get_user_and_socket_client_by_token(
    *, session_config: SessionConfiguration
) -> tuple[UserClient, SocketClient]:
    """Get user and socket client by token. Token must be set in session_config."""
    authorize_response = await _get_authorize_response(session_config=session_config)
    user_client = UserClient(session_config=session_config, login_response=authorize_response)
    socket_client = SocketClient(session_config=session_config)
    return user_client, socket_client


async def get_admin_client_by_token(*, session_config: SessionConfiguration) -> AdminClient:
    """Get admin client by token. Token must be set in session_config."""
    authorize_response = await _get_authorize_response(session_config=session_config)
    return AdminClient(session_config=session_config, login_response=authorize_response)


async def get_user_client(
    *,
    session_config: SessionConfiguration,
    username: str,
    password: str,
) -> UserClient:
    """Get a user client."""
    login_response = await get_login_response(
        session_config=session_config, username=username, password=password
    )

    return UserClient(session_config=session_config, login_response=login_response)


async def get_user_and_socket_client(
    *,
    session_config: SessionConfiguration,
    username: str,
    password: str,
) -> tuple[UserClient, SocketClient]:
    """Get user and socket client."""
    login_response = await get_login_response(
        session_config=session_config, username=username, password=password
    )

    user_client = UserClient(session_config=session_config, login_response=login_response)
    socket_client = SocketClient(session_config=session_config)
    return user_client, socket_client


async def get_admin_client(
    *,
    session_config: SessionConfiguration,
    username: str,
    password: str,
) -> UserClient:
    """Get a admin client."""
    login_response = await get_login_response(
        session_config=session_config, username=username, password=password
    )

    return AdminClient(session_config=session_config, login_response=login_response)
