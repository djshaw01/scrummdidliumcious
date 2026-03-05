"""SQLAlchemy repository adapter stubs.

Each class implements the corresponding domain repository interface but raises
:class:`NotImplementedError` for every method until the PostgreSQL adapter
work begins (Phase 6+).  The :func:`create_repositories` factory function
returns a :class:`~app.domain.repositories.RepositoryContext` compatible with
the application, so ``DATA_BACKEND=postgres`` can be selected without
additional wiring changes.
"""

from __future__ import annotations

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
from app.domain.repositories import (
    AdminConfigRepository,
    IssueRepository,
    ParticipantRepository,
    RepositoryContext,
    SessionRepository,
    TeamRepository,
    VoteRepository,
    VotingCardSetRepository,
)


class SQLAlchemyTeamRepository(TeamRepository):
    """SQLAlchemy adapter for TeamRepository — not yet implemented."""

    def list_all(self) -> list[Team]:
        raise NotImplementedError

    def get_by_id(self, id: str) -> Optional[Team]:
        raise NotImplementedError

    def create(self, team: Team) -> Team:
        raise NotImplementedError

    def update(self, team: Team) -> Team:
        raise NotImplementedError

    def delete(self, id: str) -> None:
        raise NotImplementedError


class SQLAlchemySessionRepository(SessionRepository):
    """SQLAlchemy adapter for SessionRepository — not yet implemented."""

    def list_all(self) -> list[Session]:
        raise NotImplementedError

    def get_by_id(self, id: str) -> Optional[Session]:
        raise NotImplementedError

    def list_by_team(self, team_id: str) -> list[Session]:
        raise NotImplementedError

    def get_most_recent_by_team(self, team_id: str) -> Optional[Session]:
        raise NotImplementedError

    def create(self, session: Session) -> Session:
        raise NotImplementedError

    def update(self, session: Session) -> Session:
        raise NotImplementedError

    def delete(self, id: str) -> None:
        raise NotImplementedError


class SQLAlchemyParticipantRepository(ParticipantRepository):
    """SQLAlchemy adapter for ParticipantRepository — not yet implemented."""

    def list_by_session(self, session_id: str) -> list[Participant]:
        raise NotImplementedError

    def get_by_id(self, id: str) -> Optional[Participant]:
        raise NotImplementedError

    def create(self, participant: Participant) -> Participant:
        raise NotImplementedError

    def update(self, participant: Participant) -> Participant:
        raise NotImplementedError


class SQLAlchemyIssueRepository(IssueRepository):
    """SQLAlchemy adapter for IssueRepository — not yet implemented."""

    def list_by_session(self, session_id: str) -> list[Issue]:
        raise NotImplementedError

    def get_by_id(self, id: str) -> Optional[Issue]:
        raise NotImplementedError

    def get_active_by_session(self, session_id: str) -> Optional[Issue]:
        raise NotImplementedError

    def create(self, issue: Issue) -> Issue:
        raise NotImplementedError

    def update(self, issue: Issue) -> Issue:
        raise NotImplementedError


class SQLAlchemyVoteRepository(VoteRepository):
    """SQLAlchemy adapter for VoteRepository — not yet implemented."""

    def list_by_issue(self, issue_id: str) -> list[Vote]:
        raise NotImplementedError

    def get_by_participant_and_issue(
        self, participant_id: str, issue_id: str
    ) -> Optional[Vote]:
        raise NotImplementedError

    def upsert(self, vote: Vote) -> Vote:
        raise NotImplementedError

    def delete(self, id: str) -> None:
        raise NotImplementedError

    def delete_by_issue(self, issue_id: str) -> None:
        raise NotImplementedError


class SQLAlchemyVotingCardSetRepository(VotingCardSetRepository):
    """SQLAlchemy adapter for VotingCardSetRepository — not yet implemented."""

    def list_all(self) -> list[VotingCardSet]:
        raise NotImplementedError

    def get_by_id(self, id: str) -> Optional[VotingCardSet]:
        raise NotImplementedError

    def get_default(self) -> VotingCardSet:
        raise NotImplementedError


class SQLAlchemyAdminConfigRepository(AdminConfigRepository):
    """SQLAlchemy adapter for AdminConfigRepository — not yet implemented."""

    def get(self) -> AdminConfig:
        raise NotImplementedError

    def save(self, config: AdminConfig) -> AdminConfig:
        raise NotImplementedError


def create_repositories() -> RepositoryContext:
    """Create stub SQLAlchemy repositories wrapped in a :class:`RepositoryContext`.

    Returns:
        A :class:`RepositoryContext` backed by SQLAlchemy adapters.  All
        methods raise :class:`NotImplementedError` until Phase 6+ implementation.
    """
    return RepositoryContext(
        teams=SQLAlchemyTeamRepository(),
        sessions=SQLAlchemySessionRepository(),
        participants=SQLAlchemyParticipantRepository(),
        issues=SQLAlchemyIssueRepository(),
        votes=SQLAlchemyVoteRepository(),
        card_sets=SQLAlchemyVotingCardSetRepository(),
        admin_config=SQLAlchemyAdminConfigRepository(),
    )
