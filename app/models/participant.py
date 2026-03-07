"""SQLAlchemy ORM model for Participant."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.storage_issue import StorageIssue
    from app.models.vote import Vote


class Participant(Base):
    """User involved in a SCRUM Poker session.

    :param id: Primary key UUID v4.
    :param session_id: FK to the owning Session.
    :param user_identifier: Unique user identifier within a session.
    :param display_name: Optional human-readable display name.
    :param joined_at: UTC timestamp when the participant joined.
    :param left_at: UTC timestamp when the participant left (nullable).
    :param is_leader: ``True`` when this participant is the current session leader.
    :param active_issue_id: FK to the issue currently viewed by this participant
        (nullable; deferred FK to break the participants -> storage_issues circular dep).
    """

    __tablename__ = "participants"
    __table_args__ = (
        UniqueConstraint(
            "session_id", "user_identifier", name="uq_participant_session_user"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sessions.id"), nullable=False
    )
    user_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    left_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_leader: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Deferred FK to break participants -> storage_issues dependency cycle.
    active_issue_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "storage_issues.id",
            use_alter=True,
            name="fk_participants_active_issue_id",
        ),
        nullable=True,
    )

    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="participants",
        foreign_keys=[session_id],
    )
    active_issue: Mapped["StorageIssue | None"] = relationship(
        "StorageIssue",
        foreign_keys=[active_issue_id],
        post_update=True,
    )
    votes: Mapped[list["Vote"]] = relationship("Vote", back_populates="participant")
