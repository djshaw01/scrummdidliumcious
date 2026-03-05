"""SQLAlchemy repository scaffolds for future persistence adapter swap."""

from app.domain.entities.admin_config import AdminConfig
from app.domain.entities.session import Session
from app.domain.entities.team import Team
from app.domain.entities.vote import Vote
from app.domain.repositories.admin_config_repository import AdminConfigRepository
from app.domain.repositories.session_repository import SessionRepository
from app.domain.repositories.team_repository import TeamRepository
from app.domain.repositories.vote_repository import VoteRepository


class SqlAlchemyTeamRepository(TeamRepository):
    """Placeholder SQLAlchemy implementation for team persistence."""

    def list_teams(self) -> list[Team]:
        raise NotImplementedError("SQLAlchemy adapter is implemented in a later phase.")

    def save_team(self, team: Team) -> Team:
        raise NotImplementedError("SQLAlchemy adapter is implemented in a later phase.")

    def delete_team(self, team_id: str) -> None:
        raise NotImplementedError("SQLAlchemy adapter is implemented in a later phase.")


class SqlAlchemySessionRepository(SessionRepository):
    """Placeholder SQLAlchemy implementation for session persistence."""

    def list_sessions(self) -> list[Session]:
        raise NotImplementedError("SQLAlchemy adapter is implemented in a later phase.")

    def get_session(self, session_id: str) -> Session | None:
        raise NotImplementedError("SQLAlchemy adapter is implemented in a later phase.")

    def save_session(self, session: Session) -> Session:
        raise NotImplementedError("SQLAlchemy adapter is implemented in a later phase.")


class SqlAlchemyVoteRepository(VoteRepository):
    """Placeholder SQLAlchemy implementation for vote persistence."""

    def list_votes_for_issue(self, issue_id: str) -> list[Vote]:
        raise NotImplementedError("SQLAlchemy adapter is implemented in a later phase.")

    def save_vote(self, vote: Vote) -> Vote:
        raise NotImplementedError("SQLAlchemy adapter is implemented in a later phase.")

    def clear_vote(self, issue_id: str, participant_id: str) -> None:
        raise NotImplementedError("SQLAlchemy adapter is implemented in a later phase.")


class SqlAlchemyAdminConfigRepository(AdminConfigRepository):
    """Placeholder SQLAlchemy implementation for admin config persistence."""

    def get_config(self) -> AdminConfig:
        raise NotImplementedError("SQLAlchemy adapter is implemented in a later phase.")

    def save_config(self, config: AdminConfig) -> AdminConfig:
        raise NotImplementedError("SQLAlchemy adapter is implemented in a later phase.")
