"""Exceptions for aioaudiobookshelf."""


class BadUserError(Exception):
    """Raised if this user is not suitable for the client."""


class LoginError(Exception):
    """Exception raised if login failed."""


class ApiError(Exception):
    """Exception raised if call to api failed."""


class TokenIsMissingError(Exception):
    """Exception raised if token is missing."""
