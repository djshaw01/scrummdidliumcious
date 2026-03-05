"""Seed fixture generation for in-memory repositories."""

from datetime import datetime, timezone

from app.domain.entities.admin_config import AdminConfig
from app.domain.entities.team import Team
from app.domain.entities.voting_card_set import VotingCardSet


def build_default_card_set() -> VotingCardSet:
    """Create the default voting card set required by specification.

    Returns:
        VotingCardSet with SCRUM poker defaults.
    """
    return VotingCardSet(
        id="default-fibonacci",
        name="Default Fibonacci",
        cards=["1", "2", "3", "5", "8", "13", "?", "☕️", "♾️"],
        created_at=datetime.now(timezone.utc),
    )


def build_seed_teams() -> list[Team]:
    """Create seed teams for local development.

    Returns:
        List of starter Team entities.
    """
    now = datetime.now(timezone.utc)
    return [
        Team(id="team-platform", name="Platform", is_active=True, created_at=now, updated_at=now),
        Team(id="team-product", name="Product", is_active=True, created_at=now, updated_at=now),
    ]


def build_seed_admin_config() -> AdminConfig:
    """Create a starter admin configuration.

    Returns:
        AdminConfig entity.
    """
    return AdminConfig(
        id="singleton",
        base_issue_url=None,
        theme_default="light",
        updated_at=datetime.now(timezone.utc),
    )
