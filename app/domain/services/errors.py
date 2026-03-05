"""Domain error hierarchy for business-rule and permission violations.

Raise these from service-layer methods so route handlers can translate them
into appropriate HTTP responses without leaking implementation details.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all domain-layer failures.

    Args:
        message: Human-readable description of the failure.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    """Raised when a requested entity does not exist in the repository.

    Args:
        message: Description identifying the missing resource.
    """


class ValidationError(DomainError):
    """Raised when input data violates a domain invariant.

    Args:
        message: Description of the validation rule that was broken.
    """


class ConflictError(DomainError):
    """Raised when an operation would create a conflicting state.

    Example: activating a second issue while one is already active.

    Args:
        message: Description of the conflicting state.
    """


class ForbiddenError(DomainError):
    """Raised when the requester lacks the role required for an action.

    Args:
        message: Description of the required role or permission.
    """


class NotLeaderError(ForbiddenError):
    """Raised when a non-leader participant attempts a leader-only action.

    Args:
        message: Description of the attempted action.
    """


class ParticipantLeftError(ForbiddenError):
    """Raised when a participant who has left the session attempts an action.

    Args:
        message: Description of the attempted action.
    """


class SessionCompletedError(DomainError):
    """Raised when a mutating action is attempted on a completed session.

    Args:
        message: Description of the attempted mutation.
    """


__all__ = [
    "ConflictError",
    "DomainError",
    "ForbiddenError",
    "NotFoundError",
    "NotLeaderError",
    "ParticipantLeftError",
    "SessionCompletedError",
    "ValidationError",
]
