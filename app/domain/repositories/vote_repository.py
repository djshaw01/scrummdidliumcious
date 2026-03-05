"""Vote repository interface definitions."""

from abc import ABC, abstractmethod

from app.domain.entities.vote import Vote


class VoteRepository(ABC):
    """Persistence interface for vote entities."""

    @abstractmethod
    def list_votes_for_issue(self, issue_id: str) -> list[Vote]:
        """Return votes recorded for an issue."""

    @abstractmethod
    def save_vote(self, vote: Vote) -> Vote:
        """Create or update a vote."""

    @abstractmethod
    def clear_vote(self, issue_id: str, participant_id: str) -> None:
        """Clear a participant vote for an issue."""
