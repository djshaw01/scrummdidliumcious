"""Vote entity model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Vote:
    """Represents a participant vote for an issue.

    Attributes:
        id: Unique identifier.
        session_id: Session ID.
        issue_id: Issue ID.
        participant_id: Participant ID.
        selected_card: Selected voting card.
        visibility_state: Vote visibility state.
        cast_at: Initial cast timestamp.
        updated_at: Last update timestamp.
    """

    id: str
    session_id: str
    issue_id: str
    participant_id: str
    selected_card: str
    visibility_state: str
    cast_at: datetime
    updated_at: datetime
