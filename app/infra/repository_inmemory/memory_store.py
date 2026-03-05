"""In-memory backing store used by repository adapters."""

from dataclasses import dataclass, field

from app.domain.entities.admin_config import AdminConfig
from app.domain.entities.session import Session
from app.domain.entities.team import Team
from app.domain.entities.vote import Vote


@dataclass(slots=True)
class InMemoryStore:
    """Container for mutable in-memory collections."""

    teams: dict[str, Team] = field(default_factory=dict)
    sessions: dict[str, Session] = field(default_factory=dict)
    votes_by_issue: dict[str, dict[str, Vote]] = field(default_factory=dict)
    admin_config: AdminConfig | None = None
