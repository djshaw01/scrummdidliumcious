"""Session entity model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Session:
    """Represents a time-bound estimation session.

    Attributes:
        id: Unique identifier.
        team_id: Owning team ID.
        name: Session name.
        sprint_number: Sprint identifier.
        card_set_id: Active voting card set ID.
        status: Session state (active/completed).
        leader_participant_id: Current leader participant ID.
        created_by_participant_id: Creator participant ID.
        created_at: Creation timestamp.
        completed_at: Completion timestamp, if completed.
    """

    id: str
    team_id: str
    name: str
    sprint_number: str
    card_set_id: str
    status: str
    leader_participant_id: str
    created_by_participant_id: str
    created_at: datetime
    completed_at: datetime | None = None
