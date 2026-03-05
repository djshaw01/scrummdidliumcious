"""In-memory repository adapter implementations."""

from app.domain.entities.admin_config import AdminConfig
from app.domain.entities.session import Session
from app.domain.entities.team import Team
from app.domain.entities.vote import Vote
from app.domain.repositories.admin_config_repository import AdminConfigRepository
from app.domain.repositories.session_repository import SessionRepository
from app.domain.repositories.team_repository import TeamRepository
from app.domain.repositories.vote_repository import VoteRepository
from app.infra.repository_inmemory.memory_store import InMemoryStore
from app.infra.repository_inmemory.seed_data import build_seed_admin_config


class InMemoryTeamRepository(TeamRepository):
    """Team repository backed by in-process dictionaries."""

    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def list_teams(self) -> list[Team]:
        return list(self._store.teams.values())

    def save_team(self, team: Team) -> Team:
        self._store.teams[team.id] = team
        return team

    def delete_team(self, team_id: str) -> None:
        self._store.teams.pop(team_id, None)


class InMemorySessionRepository(SessionRepository):
    """Session repository backed by in-process dictionaries."""

    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def list_sessions(self) -> list[Session]:
        return list(self._store.sessions.values())

    def get_session(self, session_id: str) -> Session | None:
        return self._store.sessions.get(session_id)

    def save_session(self, session: Session) -> Session:
        self._store.sessions[session.id] = session
        return session


class InMemoryVoteRepository(VoteRepository):
    """Vote repository backed by nested dictionaries keyed by issue/participant."""

    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def list_votes_for_issue(self, issue_id: str) -> list[Vote]:
        votes = self._store.votes_by_issue.get(issue_id, {})
        return list(votes.values())

    def save_vote(self, vote: Vote) -> Vote:
        issue_votes = self._store.votes_by_issue.setdefault(vote.issue_id, {})
        issue_votes[vote.participant_id] = vote
        return vote

    def clear_vote(self, issue_id: str, participant_id: str) -> None:
        issue_votes = self._store.votes_by_issue.get(issue_id)
        if issue_votes is None:
            return
        issue_votes.pop(participant_id, None)


class InMemoryAdminConfigRepository(AdminConfigRepository):
    """Admin configuration repository backed by in-memory state."""

    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def get_config(self) -> AdminConfig:
        if self._store.admin_config is None:
            self._store.admin_config = build_seed_admin_config()
        return self._store.admin_config

    def save_config(self, config: AdminConfig) -> AdminConfig:
        self._store.admin_config = config
        return config
