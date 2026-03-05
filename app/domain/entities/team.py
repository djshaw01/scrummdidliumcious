"""Team entity model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Team:
    """Represents a named team used to scope sessions.

    Attributes:
        id: Unique identifier.
        name: Team display name.
        is_active: Whether the team is active.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    id: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
