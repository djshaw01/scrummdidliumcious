"""SQLAlchemy ORM model for Team."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.session import Session


class Team(Base):
    """Selectable team context for poker sessions.

    :param id: Primary key UUID v4.
    :param name: Unique team display name (max 255 chars).
    :param created_at: UTC timestamp at creation.
    """

    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="team")
