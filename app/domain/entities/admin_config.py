"""Admin configuration entity model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class AdminConfig:
    """Represents workspace-level admin settings.

    Attributes:
        id: Singleton config identifier.
        base_issue_url: Optional issue URL template.
        theme_default: Optional default UI theme.
        updated_at: Last update timestamp.
    """

    id: str
    base_issue_url: str | None
    theme_default: str | None
    updated_at: datetime
