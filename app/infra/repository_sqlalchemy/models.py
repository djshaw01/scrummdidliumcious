"""SQLAlchemy 2.x ORM mapped classes mirroring the domain entity data model.

These models define the PostgreSQL schema.  The repository implementations in
:mod:`app.infra.repository_sqlalchemy.repos` use these models to fulfil the
domain repository interfaces.

Status: **scaffolded** — models are fully defined; repository methods are
implemented in a later phase when ``DATA_BACKEND=postgres`` is activated.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy ORM models."""


class TeamModel(Base):
    """ORM mapping for the ``teams`` table."""

    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    sessions: Mapped[list[SessionModel]] = relationship(
        "SessionModel", back_populates="team", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TeamModel id={self.id!r} name={self.name!r}>"


class VotingCardSetModel(Base):
    """ORM mapping for the ``voting_card_sets`` table."""

    __tablename__ = "voting_card_sets"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    cards_csv: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Comma-separated ordered card value strings.",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return f"<VotingCardSetModel id={self.id!r} name={self.name!r}>"


class AdminConfigModel(Base):
    """ORM mapping for the singleton ``admin_config`` table."""

    __tablename__ = "admin_config"

    id: Mapped[str] = mapped_column(String, primary_key=True, default="config")
    base_issue_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    theme_default: Mapped[str] = mapped_column(String, default="light", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return f"<AdminConfigModel base_issue_url={self.base_issue_url!r}>"


class SessionModel(Base):
    """ORM mapping for the ``sessions`` table."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    team_id: Mapped[str] = mapped_column(ForeignKey("teams.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    sprint_number: Mapped[str] = mapped_column(String, nullable=False)
    card_set_id: Mapped[str] = mapped_column(
        ForeignKey("voting_card_sets.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String, default="active", nullable=False)
    leader_participant_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_by_participant_id: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    team: Mapped[TeamModel] = relationship("TeamModel", back_populates="sessions")
    participants: Mapped[list[ParticipantModel]] = relationship(
        "ParticipantModel", back_populates="session", cascade="all, delete-orphan"
    )
    issues: Mapped[list[IssueModel]] = relationship(
        "IssueModel", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SessionModel id={self.id!r} name={self.name!r} status={self.status!r}>"


class ParticipantModel(Base):
    """ORM mapping for the ``participants`` table."""

    __tablename__ = "participants"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    initials: Mapped[str] = mapped_column(String, nullable=False)
    is_leader: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    join_state: Mapped[str] = mapped_column(String, default="joined", nullable=False)
    evaluation_state: Mapped[str] = mapped_column(
        String, default="active_issue_participating", nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    left_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    session: Mapped[SessionModel] = relationship(
        "SessionModel", back_populates="participants"
    )
    votes: Mapped[list[VoteModel]] = relationship(
        "VoteModel", back_populates="participant", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ParticipantModel id={self.id!r} display_name={self.display_name!r}>"


class IssueModel(Base):
    """ORM mapping for the ``issues`` table."""

    __tablename__ = "issues"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    issue_type: Mapped[str] = mapped_column(String, nullable=False)
    issue_key: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prior_estimate: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    final_estimate: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revealed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    session: Mapped[SessionModel] = relationship("SessionModel", back_populates="issues")
    votes: Mapped[list[VoteModel]] = relationship(
        "VoteModel", back_populates="issue", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<IssueModel id={self.id!r} issue_key={self.issue_key!r}>"


class VoteModel(Base):
    """ORM mapping for the ``votes`` table."""

    __tablename__ = "votes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    issue_id: Mapped[str] = mapped_column(ForeignKey("issues.id"), nullable=False)
    participant_id: Mapped[str] = mapped_column(
        ForeignKey("participants.id"), nullable=False
    )
    selected_card: Mapped[str] = mapped_column(String, nullable=False)
    visibility_state: Mapped[str] = mapped_column(
        String, default="hidden", nullable=False
    )
    cast_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    issue: Mapped[IssueModel] = relationship("IssueModel", back_populates="votes")
    participant: Mapped[ParticipantModel] = relationship(
        "ParticipantModel", back_populates="votes"
    )

    def __repr__(self) -> str:
        return (
            f"<VoteModel id={self.id!r} participant_id={self.participant_id!r}"
            f" selected_card={self.selected_card!r}>"
        )
