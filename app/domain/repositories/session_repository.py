"""Session repository interface definitions."""

from abc import ABC, abstractmethod

from app.domain.entities.session import Session


class SessionRepository(ABC):
    """Persistence interface for session aggregates."""

    @abstractmethod
    def list_sessions(self) -> list[Session]:
        """Return all sessions ordered by repository policy."""

    @abstractmethod
    def get_session(self, session_id: str) -> Session | None:
        """Return one session by ID if present."""

    @abstractmethod
    def save_session(self, session: Session) -> Session:
        """Create or update a session."""
