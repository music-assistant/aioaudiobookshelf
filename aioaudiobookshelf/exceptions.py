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


class TokenNotRenewableError(AbsAuthError):
    """Raised if abs rejected the token and there is nothing to renew it with.

    An api key or a pre v2.26 token cannot be refreshed. Abs deactivates an
    expired api key, see its auth/TokenManager.js.
    """


class AbsApiError(AbsError):
    """Base exception for API call errors."""


class ApiError(AbsApiError):
    """Exception raised if call to api failed."""


class SchemaError(ApiError):
    """Raised when abs' answer does not match the schema.

    Either abs changed what it sends, or our schema was wrong about it. Inherits
    from ApiError so that a caller which catches that keeps catching this.
    """


class ServiceUnavailableError(AbsApiError):
    """Raised if service is not available."""


class NotFoundError(AbsApiError):
    """Raised when we get a 404."""


class SessionNotFoundError(NotFoundError):
    """Specified session was not found."""


class SessionSyncError(AbsError):
    """Error while syncing (a) session(s)."""


class SessionSyncNotFoundError(SessionSyncError, SessionNotFoundError):
    """Raised if the session to sync is gone, e.g. after an abs restart.

    Inherits from both, so callers which only know SessionSyncError keep working.
    """
