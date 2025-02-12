"""Client library for Audiobookshelf."""

from aiohttp.client_exceptions import ClientResponseError, InvalidUrlClientError

from aioaudiobookshelf.client import AdminClient, SessionConfiguration, SocketClient, UserClient
from aioaudiobookshelf.exceptions import LoginError
from aioaudiobookshelf.schema.calls_login import LoginParameters, LoginResponse

__version__ = "0.1.0"


async def _get_login_response(
    *, session_config: SessionConfiguration, username: str, password: str
) -> LoginResponse:
    login_request = LoginParameters(username=username, password=password).to_dict()

    try:
        resp = await session_config.session.post(
            f"{session_config.url}/login",
            json=login_request,
            ssl=session_config.verify_ssl,
            raise_for_status=True,
        )
    except (ClientResponseError, InvalidUrlClientError) as exc:
        raise LoginError from exc
    return LoginResponse.from_json(await resp.read())


async def get_user_client(
    *,
    session_config: SessionConfiguration,
    username: str,
    password: str,
) -> UserClient:
    """Get a user client."""
    login_response = await _get_login_response(
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
    login_response = await _get_login_response(
        session_config=session_config, username=username, password=password
    )

    user_client = UserClient(session_config=session_config, login_response=login_response)
    if not session_config.token:
        session_config.token = user_client.token
    socket_client = SocketClient(session_config=session_config)
    return user_client, socket_client


async def get_admin_client(
    *,
    session_config: SessionConfiguration,
    username: str,
    password: str,
) -> UserClient:
    """Get a admin client."""
    login_response = await _get_login_response(
        session_config=session_config, username=username, password=password
    )

    return AdminClient(session_config=session_config, login_response=login_response)
