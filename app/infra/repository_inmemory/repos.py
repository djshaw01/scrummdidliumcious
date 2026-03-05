"""In-memory repository implementations for all domain entities.

Each class holds its data in a plain Python dict keyed by entity ID.
Instances are created fresh per application startup via
:func:`create_repositories` and attached to ``app.extensions["repos"]`` by
:func:`app.infra.init_repositories`.
"""

from __future__ import annotations

from typing import Optional

from app.domain.entities import (
    AdminConfig,
    Issue,
    Participant,
    Session,
    VotingCardSet,
    Team,
    Vote,
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


class InMemoryTeamRepository(TeamRepository):
    """Dict-backed implementation of :class:`TeamRepository`."""

    def __init__(self) -> None:
        self._store: dict[str, Team] = {}

    def list_all(self) -> list[Team]:
        """Return all teams ordered by creation time ascending."""
        return sorted(self._store.values(), key=lambda t: t.created_at)

    def get_by_id(self, id: str) -> Optional[Team]:
        """Return team by ID or ``None``."""
        return self._store.get(id)

    def create(self, team: Team) -> Team:
        """Store a new team and return it."""
        self._store[team.id] = team
        return team

    def update(self, team: Team) -> Team:
        """Overwrite an existing team record and return it."""
        self._store[team.id] = team
        return team

    def delete(self, id: str) -> None:
        """Remove team by ID (no-op if absent)."""
        self._store.pop(id, None)


class InMemorySessionRepository(SessionRepository):
    """Dict-backed implementation of :class:`SessionRepository`."""

    def __init__(self) -> None:
        self._store: dict[str, Session] = {}

    def list_all(self) -> list[Session]:
        """Return all sessions ordered by creation time descending."""
        return sorted(self._store.values(), key=lambda s: s.created_at, reverse=True)

    def get_by_id(self, id: str) -> Optional[Session]:
        """Return session by ID or ``None``."""
        return self._store.get(id)

    def list_by_team(self, team_id: str) -> list[Session]:
        """Return sessions for a team, most-recent first."""
        return sorted(
            [s for s in self._store.values() if s.team_id == team_id],
            key=lambda s: s.created_at,
            reverse=True,
        )

    def get_most_recent_by_team(self, team_id: str) -> Optional[Session]:
        """Return the most recently created session for a team, or ``None``."""
        sessions = self.list_by_team(team_id)
        return sessions[0] if sessions else None

    def create(self, session: Session) -> Session:
        """Store a new session and return it."""
        self._store[session.id] = session
        return session

    def update(self, session: Session) -> Session:
        """Overwrite an existing session record and return it."""
        self._store[session.id] = session
        return session

    def delete(self, id: str) -> None:
        """Remove session by ID (no-op if absent)."""
        self._store.pop(id, None)


class InMemoryParticipantRepository(ParticipantRepository):
    """Dict-backed implementation of :class:`ParticipantRepository`."""

    def __init__(self) -> None:
        self._store: dict[str, Participant] = {}

    def list_by_session(self, session_id: str) -> list[Participant]:
        """Return participants for a session ordered by join time ascending."""
        return sorted(
            [p for p in self._store.values() if p.session_id == session_id],
            key=lambda p: p.joined_at,
        )

    def get_by_id(self, id: str) -> Optional[Participant]:
        """Return participant by ID or ``None``."""
        return self._store.get(id)

    def create(self, participant: Participant) -> Participant:
        """Store a new participant and return it."""
        self._store[participant.id] = participant
        return participant

    def update(self, participant: Participant) -> Participant:
        """Overwrite an existing participant record and return it."""
        self._store[participant.id] = participant
        return participant


class InMemoryIssueRepository(IssueRepository):
    """Dict-backed implementation of :class:`IssueRepository`."""

    def __init__(self) -> None:
        self._store: dict[str, Issue] = {}

    def list_by_session(self, session_id: str) -> list[Issue]:
        """Return issues for a session ordered by ``order_index`` ascending."""
        return sorted(
            [i for i in self._store.values() if i.session_id == session_id],
            key=lambda i: i.order_index,
        )

    def get_by_id(self, id: str) -> Optional[Issue]:
        """Return issue by ID or ``None``."""
        return self._store.get(id)

    def get_active_by_session(self, session_id: str) -> Optional[Issue]:
        """Return the single ``is_active=True`` issue for a session, or ``None``."""
        for issue in self._store.values():
            if issue.session_id == session_id and issue.is_active:
                return issue
        return None

    def create(self, issue: Issue) -> Issue:
        """Store a new issue and return it."""
        self._store[issue.id] = issue
        return issue

    def update(self, issue: Issue) -> Issue:
        """Overwrite an existing issue record and return it."""
        self._store[issue.id] = issue
        return issue


class InMemoryVoteRepository(VoteRepository):
    """Dict-backed implementation of :class:`VoteRepository`."""

    def __init__(self) -> None:
        self._store: dict[str, Vote] = {}

    def list_by_issue(self, issue_id: str) -> list[Vote]:
        """Return votes for an issue ordered by cast time ascending."""
        return sorted(
            [v for v in self._store.values() if v.issue_id == issue_id],
            key=lambda v: v.cast_at,
        )

    def get_by_participant_and_issue(
        self, participant_id: str, issue_id: str
    ) -> Optional[Vote]:
        """Return a participant's active vote for an issue, or ``None``."""
        for vote in self._store.values():
            if vote.participant_id == participant_id and vote.issue_id == issue_id:
                return vote
        return None

    def upsert(self, vote: Vote) -> Vote:
        """Create or replace a vote (deduplicated by participant + issue)."""
        existing = self.get_by_participant_and_issue(vote.participant_id, vote.issue_id)
        if existing is not None:
            self._store.pop(existing.id, None)
        self._store[vote.id] = vote
        return vote

    def delete(self, id: str) -> None:
        """Remove vote by ID (no-op if absent)."""
        self._store.pop(id, None)

    def delete_by_issue(self, issue_id: str) -> None:
        """Remove all votes for an issue."""
        ids = [v.id for v in self._store.values() if v.issue_id == issue_id]
        for id in ids:
            self._store.pop(id, None)


class InMemoryVotingCardSetRepository(VotingCardSetRepository):
    """Dict-backed implementation of :class:`VotingCardSetRepository`."""

    def __init__(self) -> None:
        self._store: dict[str, VotingCardSet] = {}
        default = VotingCardSet.make_default()
        self._store[default.id] = default

    def list_all(self) -> list[VotingCardSet]:
        """Return all card sets ordered by creation time ascending."""
        return sorted(self._store.values(), key=lambda c: c.created_at)

    def get_by_id(self, id: str) -> Optional[VotingCardSet]:
        """Return card set by ID or ``None``."""
        return self._store.get(id)

    def get_default(self) -> VotingCardSet:
        """Return the default Fibonacci-extended card set."""
        return self._store["cardset-default"]


class InMemoryAdminConfigRepository(AdminConfigRepository):
    """Single-record implementation of :class:`AdminConfigRepository`."""

    def __init__(self) -> None:
        self._config: AdminConfig = AdminConfig()

    def get(self) -> AdminConfig:
        """Return the current admin configuration."""
        return self._config

    def save(self, config: AdminConfig) -> AdminConfig:
        """Overwrite the admin configuration and return it."""
        self._config = config
        return self._config


def create_repositories() -> RepositoryContext:
    """Create and return a fresh set of in-memory repository instances.

    Returns:
        A :class:`RepositoryContext` with all seven in-memory adapters
        populated. Call :func:`app.infra.repository_inmemory.seed.seed_repositories`
        on the returned context to load development fixture data.
    """
    return RepositoryContext(
        teams=InMemoryTeamRepository(),
        sessions=InMemorySessionRepository(),
        participants=InMemoryParticipantRepository(),
        issues=InMemoryIssueRepository(),
        votes=InMemoryVoteRepository(),
        card_sets=InMemoryVotingCardSetRepository(),
        admin_config=InMemoryAdminConfigRepository(),
    )
