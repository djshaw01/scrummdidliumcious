"""SQLAlchemy ORM model for Configuration (singleton row)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Configuration(Base):
    """Global operational settings stored as a singleton row (id always 1).

    :param id: Integer primary key; always ``1`` for the singleton row.
    :param base_url_for_issues: Optional absolute URL prefix for issue key hyperlinks.
    :param default_theme: Optional default theme (``light`` or ``dark``).
    :param updated_at: UTC timestamp of last configuration update.
    """

    __tablename__ = "configuration"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    base_url_for_issues: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    default_theme: Mapped[str | None] = mapped_column(
        Enum("light", "dark", name="theme_enum"),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
