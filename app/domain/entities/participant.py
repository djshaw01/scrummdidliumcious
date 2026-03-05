"""Participant entity model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Participant:
    """Represents a user participating in a session.

    Attributes:
        id: Unique identifier.
        session_id: Parent session ID.
        display_name: Participant display name.
        initials: Short initials used in UI badges.
        is_leader: Whether participant is session leader.
        join_state: Join state (joined/left).
        evaluation_state: Participation state for active evaluation.
        joined_at: Join timestamp.
        left_at: Optional leave timestamp.
    """

    id: str
    session_id: str
    display_name: str
    initials: str
    is_leader: bool
    join_state: str
    evaluation_state: str
    joined_at: datetime
    left_at: datetime | None = None
