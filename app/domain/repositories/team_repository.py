"""Team repository interface definitions."""

from abc import ABC, abstractmethod

from app.domain.entities.team import Team


class TeamRepository(ABC):
    """Persistence interface for team entities."""

    @abstractmethod
    def list_teams(self) -> list[Team]:
        """Return all teams."""

    @abstractmethod
    def save_team(self, team: Team) -> Team:
        """Create or update a team."""

    @abstractmethod
    def delete_team(self, team_id: str) -> None:
        """Delete a team by ID."""
