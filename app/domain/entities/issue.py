"""Issue entity model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Issue:
    """Represents an imported backlog item.

    Attributes:
        id: Unique identifier.
        session_id: Parent session ID.
        order_index: List ordering index.
        issue_type: Issue type (Story/Bug).
        issue_key: External issue key.
        summary: Issue summary.
        description: Optional detailed description.
        prior_estimate: Optional historical estimate.
        final_estimate: Optional finalized estimate.
        is_active: Whether this issue is active.
        revealed_at: Optional reveal timestamp.
    """

    id: str
    session_id: str
    order_index: int
    issue_type: str
    issue_key: str
    summary: str
    description: str | None
    prior_estimate: str | None
    final_estimate: str | None
    is_active: bool
    revealed_at: datetime | None = None
