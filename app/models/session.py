"""SQLAlchemy ORM model for Session."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.participant import Participant
    from app.models.storage_issue import StorageIssue
    from app.models.team import Team


class Session(Base):
    """SCRUM Poker session lifecycle entity.

    :param id: Primary key UUID v4.
    :param name: Session display name.
    :param team_id: FK to the owning Team.
    :param sprint_number: Sprint iteration number (positive integer).
    :param status: Lifecycle state; one of ``active``, ``completed``.
    :param leader_participant_id: FK to the current session leader Participant
        (nullable until first participant joins; deferred FK to break circular dep).
    :param card_set_name: Estimation card set used; default ``fibonacci_plus_specials``.
    :param created_at: UTC creation timestamp.
    :param completed_at: UTC completion timestamp; set when status -> ``completed``.
    """

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id"), nullable=False
    )
    sprint_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("active", "completed", name="session_status_enum"),
        nullable=False,
        default="active",
    )
    # Deferred FK (use_alter) to break the sessions <-> participants circular dep.
    leader_participant_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "participants.id",
            use_alter=True,
            name="fk_sessions_leader_participant_id",
        ),
        nullable=True,
    )
    card_set_name: Mapped[str] = mapped_column(
        String(100), nullable=False, default="fibonacci_plus_specials"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    team: Mapped["Team"] = relationship("Team", back_populates="sessions")
    participants: Mapped[list["Participant"]] = relationship(
        "Participant",
        back_populates="session",
        foreign_keys="[Participant.session_id]",
    )
    issues: Mapped[list["StorageIssue"]] = relationship(
        "StorageIssue", back_populates="session"
    )
    leader: Mapped["Participant | None"] = relationship(
        "Participant",
        foreign_keys=[leader_participant_id],
        post_update=True,
    )
