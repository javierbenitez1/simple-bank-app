class NotFoundError(Exception):
    """Raised when a user or account doesn't exist."""


class BusinessRuleError(Exception):
    """Raised when a request breaks a banking rule."""


class ConflictError(Exception):
    """Raised when something already exists (like a duplicate email)."""

class UnauthorizedError(Exception):
    """Missing, invalid, or expired login."""


class ForbiddenError(Exception):
    """Logged in, but not allowed to do this."""
