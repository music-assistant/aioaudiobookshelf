"""Exceptions for aioaudiobookshelf."""


class AbsError(Exception):
    """Base exception for aioaudiobookshelf."""


class AbsAuthError(AbsError):
    """Base exception for authentication and authorization errors."""


class BadUserError(AbsAuthError):
    """Raised if this user is not suitable for the client."""


class LoginError(AbsAuthError):
    """Exception raised if login failed."""


class TokenIsMissingError(AbsAuthError):
    """Exception raised if token is missing."""


class AccessTokenExpiredError(AbsAuthError):
    """Exception raised if access token expired."""


class RefreshTokenExpiredError(AbsAuthError):
    """Exception raised if refresh token expired."""


class AbsApiError(AbsError):
    """Base exception for API call errors."""


class ApiError(AbsApiError):
    """Exception raised if call to api failed."""


class ServiceUnavailableError(AbsApiError):
    """Raised if service is not available."""


class NotFoundError(AbsApiError):
    """Raised when we get a 404."""


class SessionNotFoundError(NotFoundError):
    """Specified session was not found."""


class SessionSyncError(Exception):
    """Error while syncing (a) session(s)."""
