"""Exceptions for aioaudiobookshelf."""


class BadUserError(Exception):
    """Raised if this user is not suitable for the client."""


class LoginError(Exception):
    """Exception raised if login failed."""
