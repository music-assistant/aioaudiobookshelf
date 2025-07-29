"""Exceptions for aioaudiobookshelf."""


class BadUserError(Exception):
    """Raised if this user is not suitable for the client."""


class LoginError(Exception):
    """Exception raised if login failed."""


class ApiError(Exception):
    """Exception raised if call to api failed."""


class TokenIsMissingError(Exception):
    """Exception raised if token is missing."""


class AccessTokenExpiredError(Exception):
    """Exception raised if access token expired."""


class RefreshTokenExpiredError(Exception):
    """Exception raised if refresh token expired."""


class ServiceUnavailableError(Exception):
    """Raised if service is not available."""
