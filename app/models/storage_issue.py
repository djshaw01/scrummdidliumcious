"""SQLAlchemy ORM model for StorageIssue."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.vote import Vote


class StorageIssue(Base):
    """SCRUM issue or story imported into a session for estimation.

    :param id: Primary key UUID v4.
    :param session_id: FK to the owning Session.
    :param issue_type: Issue category; one of ``Story``, ``Bug``.
    :param issue_key: Unique identifier for the issue within the session (e.g. ``PROJ-123``).
    :param summary: Short one-line issue title.
    :param description: Optional longer issue description.
    :param uploaded_story_points: Story point value from the uploaded CSV, if present.
    :param final_estimate: Leader-selected or custom estimate saved after reveal.
    :param is_active: ``True`` when this is the issue currently under active vote.
    :param revealed_at: UTC timestamp set on leader reveal; guards against further voting.
    :param created_at: UTC creation timestamp.
    """

    __tablename__ = "storage_issues"
    __table_args__ = (
        UniqueConstraint("session_id", "issue_key", name="uq_issue_session_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sessions.id"), nullable=False
    )
    issue_type: Mapped[str] = mapped_column(
        Enum("Story", "Bug", name="issue_type_enum"), nullable=False
    )
    issue_key: Mapped[str] = mapped_column(String(100), nullable=False)
    summary: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_story_points: Mapped[str | None] = mapped_column(String(50), nullable=True)
    final_estimate: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    revealed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    session: Mapped["Session"] = relationship("Session", back_populates="issues")
    votes: Mapped[list["Vote"]] = relationship("Vote", back_populates="issue")
