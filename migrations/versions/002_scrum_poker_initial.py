"""Create SCRUM Poker schema: teams, sessions, participants, storage_issues, votes, configuration.

Revision ID: 002_scrum_poker_initial
Revises:
Create Date: 2026-03-06

This migration creates all tables required for the SCRUM Poker feature.
Circular foreign keys (sessions.leader_participant_id -> participants and
participants.active_issue_id -> storage_issues) are added as deferred
constraints after both referenced tables exist.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "002_scrum_poker_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all SCRUM Poker tables and deferred cross-table foreign keys."""

    # ── teams ─────────────────────────────────────────────────────────────────
    op.create_table(
        "teams",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # ── sessions (leader_participant_id FK deferred — participants not yet created)
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("sprint_number", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "completed", name="session_status_enum"),
            nullable=False,
        ),
        sa.Column("leader_participant_id", sa.Uuid(), nullable=True),
        sa.Column("card_set_name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── participants (active_issue_id FK deferred — storage_issues not yet created)
    op.create_table(
        "participants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("user_identifier", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_leader", sa.Boolean(), nullable=False),
        sa.Column("active_issue_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "session_id", "user_identifier", name="uq_participant_session_user"
        ),
    )

    # ── storage_issues ────────────────────────────────────────────────────────
    op.create_table(
        "storage_issues",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column(
            "issue_type",
            sa.Enum("Story", "Bug", name="issue_type_enum"),
            nullable=False,
        ),
        sa.Column("issue_key", sa.String(100), nullable=False),
        sa.Column("summary", sa.String(512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("uploaded_story_points", sa.String(50), nullable=True),
        sa.Column("final_estimate", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("revealed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "issue_key", name="uq_issue_session_key"),
    )

    # ── deferred FK: sessions.leader_participant_id -> participants.id ─────────
    op.create_foreign_key(
        "fk_sessions_leader_participant_id",
        "sessions",
        "participants",
        ["leader_participant_id"],
        ["id"],
    )

    # ── deferred FK: participants.active_issue_id -> storage_issues.id ────────
    op.create_foreign_key(
        "fk_participants_active_issue_id",
        "participants",
        "storage_issues",
        ["active_issue_id"],
        ["id"],
    )

    # ── votes ─────────────────────────────────────────────────────────────────
    op.create_table(
        "votes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("issue_id", sa.Uuid(), nullable=False),
        sa.Column("participant_id", sa.Uuid(), nullable=False),
        sa.Column("card_value", sa.String(10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["storage_issues.id"]),
        sa.ForeignKeyConstraint(["participant_id"], ["participants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "issue_id", "participant_id", name="uq_vote_issue_participant"
        ),
    )

    # ── configuration (singleton) ─────────────────────────────────────────────
    op.create_table(
        "configuration",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("base_url_for_issues", sa.String(2048), nullable=True),
        sa.Column(
            "default_theme",
            sa.Enum("light", "dark", name="theme_enum"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop all SCRUM Poker tables and their associated enum types."""

    op.drop_table("configuration")
    op.drop_table("votes")
    op.drop_constraint(
        "fk_participants_active_issue_id", "participants", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_sessions_leader_participant_id", "sessions", type_="foreignkey"
    )
    op.drop_table("storage_issues")
    op.drop_table("participants")
    op.drop_table("sessions")
    op.drop_table("teams")

    # Drop PostgreSQL-native enum types created during upgrade.
    op.execute("DROP TYPE IF EXISTS session_status_enum")
    op.execute("DROP TYPE IF EXISTS issue_type_enum")
    op.execute("DROP TYPE IF EXISTS theme_enum")
