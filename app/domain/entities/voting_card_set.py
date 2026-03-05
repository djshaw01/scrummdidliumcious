"""Voting card set entity model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class VotingCardSet:
    """Represents an allowed collection of voting cards.

    Attributes:
        id: Unique identifier.
        name: Card set name.
        cards: Ordered card values.
        created_at: Creation timestamp.
    """

    id: str
    name: str
    cards: list[str]
    created_at: datetime
