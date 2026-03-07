"""SQLAlchemy ORM model for Vote."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.participant import Participant
    from app.models.storage_issue import StorageIssue

#: Card values permitted by the fibonacci_plus_specials deck.
VALID_CARD_VALUES: frozenset[str] = frozenset(
    {"1", "2", "3", "5", "8", "13", "?", "\u2615", "\u267e"}
)


class Vote(Base):
    """Latest vote cast by a participant for a specific issue.

    :param id: Primary key UUID v4.
    :param issue_id: FK to the StorageIssue being estimated.
    :param participant_id: FK to the voting Participant.
    :param card_value: Selected estimation card value (one of :data:`VALID_CARD_VALUES`).
    :param created_at: UTC timestamp of initial vote.
    :param updated_at: UTC timestamp of most recent update (upsert).
    """

    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint(
            "issue_id", "participant_id", name="uq_vote_issue_participant"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    issue_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("storage_issues.id"), nullable=False
    )
    participant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("participants.id"), nullable=False
    )
    card_value: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    issue: Mapped["StorageIssue"] = relationship("StorageIssue", back_populates="votes")
    participant: Mapped["Participant"] = relationship(
        "Participant", back_populates="votes"
    )
