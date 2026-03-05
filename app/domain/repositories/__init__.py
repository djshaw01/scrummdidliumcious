"""Repository interfaces defining the persistence contract for all domain entities.

Each abstract class defines the operations a storage adapter must implement.
The :class:`RepositoryContext` groups all repos so route handlers and services
can receive a single dependency rather than importing each repo individually.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from app.domain.entities import (
    AdminConfig,
    Issue,
    Participant,
    Session,
    Team,
    Vote,
    VotingCardSet,
)


class TeamRepository(ABC):
    """Persistence contract for :class:`~app.domain.entities.Team` records."""

    @abstractmethod
    def list_all(self) -> list[Team]:
        """Return all teams ordered by creation time ascending."""

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Team]:
        """Return the team with the given ID, or ``None`` if not found.

        Args:
            id: UUID string of the team to retrieve.
        """

    @abstractmethod
    def create(self, team: Team) -> Team:
        """Persist a new team and return it.

        Args:
            team: Fully populated :class:`Team` instance to store.
        """

    @abstractmethod
    def update(self, team: Team) -> Team:
        """Overwrite an existing team record and return it.

        Args:
            team: :class:`Team` instance whose ``id`` already exists in the store.
        """

    @abstractmethod
    def delete(self, id: str) -> None:
        """Remove the team with the given ID (no-op if not found).

        Args:
            id: UUID string of the team to remove.
        """


class SessionRepository(ABC):
    """Persistence contract for :class:`~app.domain.entities.Session` records."""

    @abstractmethod
    def list_all(self) -> list[Session]:
        """Return all sessions ordered by creation time descending (most recent first)."""

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Session]:
        """Return the session with the given ID, or ``None`` if not found.

        Args:
            id: UUID string of the session to retrieve.
        """

    @abstractmethod
    def list_by_team(self, team_id: str) -> list[Session]:
        """Return sessions for a team ordered by creation time descending.

        Args:
            team_id: UUID string of the parent team.
        """

    @abstractmethod
    def get_most_recent_by_team(self, team_id: str) -> Optional[Session]:
        """Return the most recently created session for a team, or ``None``.

        Args:
            team_id: UUID string of the parent team.
        """

    @abstractmethod
    def create(self, session: Session) -> Session:
        """Persist a new session and return it.

        Args:
            session: Fully populated :class:`Session` instance to store.
        """

    @abstractmethod
    def update(self, session: Session) -> Session:
        """Overwrite an existing session record and return it.

        Args:
            session: :class:`Session` instance whose ``id`` already exists.
        """

    @abstractmethod
    def delete(self, id: str) -> None:
        """Remove the session with the given ID (no-op if not found).

        Args:
            id: UUID string of the session to remove.
        """


class ParticipantRepository(ABC):
    """Persistence contract for :class:`~app.domain.entities.Participant` records."""

    @abstractmethod
    def list_by_session(self, session_id: str) -> list[Participant]:
        """Return all participants for a session ordered by join time ascending.

        Args:
            session_id: UUID string of the parent session.
        """

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Participant]:
        """Return the participant with the given ID, or ``None``.

        Args:
            id: UUID string of the participant to retrieve.
        """

    @abstractmethod
    def create(self, participant: Participant) -> Participant:
        """Persist a new participant and return it.

        Args:
            participant: Fully populated :class:`Participant` instance to store.
        """

    @abstractmethod
    def update(self, participant: Participant) -> Participant:
        """Overwrite an existing participant record and return it.

        Args:
            participant: :class:`Participant` instance whose ``id`` already exists.
        """


class IssueRepository(ABC):
    """Persistence contract for :class:`~app.domain.entities.Issue` records."""

    @abstractmethod
    def list_by_session(self, session_id: str) -> list[Issue]:
        """Return all issues for a session ordered by ``order_index`` ascending.

        Args:
            session_id: UUID string of the parent session.
        """

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Issue]:
        """Return the issue with the given ID, or ``None``.

        Args:
            id: UUID string of the issue to retrieve.
        """

    @abstractmethod
    def get_active_by_session(self, session_id: str) -> Optional[Issue]:
        """Return the single active issue in a session, or ``None``.

        Args:
            session_id: UUID string of the target session.
        """

    @abstractmethod
    def create(self, issue: Issue) -> Issue:
        """Persist a new issue and return it.

        Args:
            issue: Fully populated :class:`Issue` instance to store.
        """

    @abstractmethod
    def update(self, issue: Issue) -> Issue:
        """Overwrite an existing issue record and return it.

        Args:
            issue: :class:`Issue` instance whose ``id`` already exists.
        """


class VoteRepository(ABC):
    """Persistence contract for :class:`~app.domain.entities.Vote` records."""

    @abstractmethod
    def list_by_issue(self, issue_id: str) -> list[Vote]:
        """Return all votes for an issue ordered by cast time ascending.

        Args:
            issue_id: UUID string of the target issue.
        """

    @abstractmethod
    def get_by_participant_and_issue(
        self, participant_id: str, issue_id: str
    ) -> Optional[Vote]:
        """Return the active vote for a participant–issue pair, or ``None``.

        Args:
            participant_id: UUID string of the voting participant.
            issue_id: UUID string of the issue being voted on.
        """

    @abstractmethod
    def upsert(self, vote: Vote) -> Vote:
        """Create or replace a vote record (keyed on participant + issue) and return it.

        Args:
            vote: :class:`Vote` instance to create or update.
        """

    @abstractmethod
    def delete(self, id: str) -> None:
        """Remove a vote by its ID (no-op if not found).

        Args:
            id: UUID string of the vote to remove.
        """

    @abstractmethod
    def delete_by_issue(self, issue_id: str) -> None:
        """Remove all votes for an issue (used when resetting a voting round).

        Args:
            issue_id: UUID string of the issue whose votes should be cleared.
        """


class VotingCardSetRepository(ABC):
    """Persistence contract for :class:`~app.domain.entities.VotingCardSet` records."""

    @abstractmethod
    def list_all(self) -> list[VotingCardSet]:
        """Return all available voting card sets."""

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[VotingCardSet]:
        """Return the card set with the given ID, or ``None``.

        Args:
            id: UUID string of the card set to retrieve.
        """

    @abstractmethod
    def get_default(self) -> VotingCardSet:
        """Return the default Fibonacci-extended card set."""


class AdminConfigRepository(ABC):
    """Persistence contract for the singleton :class:`~app.domain.entities.AdminConfig`."""

    @abstractmethod
    def get(self) -> AdminConfig:
        """Return the current workspace admin configuration."""

    @abstractmethod
    def save(self, config: AdminConfig) -> AdminConfig:
        """Persist an updated admin configuration and return it.

        Args:
            config: Updated :class:`AdminConfig` instance to store.
        """


@dataclass
class RepositoryContext:
    """Container holding one instance of each repository.

    Pass this object to services and route handlers instead of injecting
    individual repositories, keeping function signatures concise.

    Attributes:
        teams: Team persistence adapter.
        sessions: Session persistence adapter.
        participants: Participant persistence adapter.
        issues: Issue persistence adapter.
        votes: Vote persistence adapter.
        card_sets: VotingCardSet persistence adapter.
        admin_config: AdminConfig persistence adapter.
    """

    teams: TeamRepository
    sessions: SessionRepository
    participants: ParticipantRepository
    issues: IssueRepository
    votes: VoteRepository
    card_sets: VotingCardSetRepository
    admin_config: AdminConfigRepository


__all__ = [
    "AdminConfigRepository",
    "IssueRepository",
    "ParticipantRepository",
    "RepositoryContext",
    "SessionRepository",
    "TeamRepository",
    "VoteRepository",
    "VotingCardSetRepository",
]

