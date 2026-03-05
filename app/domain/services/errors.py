"""Shared domain errors and validation primitives."""


class DomainError(Exception):
    """Base error for domain rule violations."""


class NotFoundError(DomainError):
    """Raised when a requested entity does not exist."""


class ValidationError(DomainError):
    """Raised when a domain invariant is violated."""


class AuthorizationError(DomainError):
    """Raised when an actor does not have permission for an action."""


def ensure(condition: bool, message: str) -> None:
    """Assert a domain condition and raise ValidationError when it fails.

    Args:
        condition: Condition that must evaluate to True.
        message: Validation error message.

    Returns:
        None.
    """
    if not condition:
        raise ValidationError(message)
