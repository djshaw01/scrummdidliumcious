"""Development seed fixtures for the in-memory repositories.

Call :func:`seed_repositories` once after :func:`~.repos.create_repositories`
to populate realistic demo data covering active and completed sessions, multiple
teams, issues in various states, and a pair of hidden votes ready for reveal.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.domain.entities import (
    AdminConfig,
    Issue,
    IssueType,
    JoinState,
    Participant,
    Session,
    SessionStatus,
    Team,
    ThemePreference,
    Vote,
)
from app.domain.repositories import RepositoryContext


def _ago(days: int = 0, hours: int = 0, minutes: int = 0) -> datetime:
    """Return a UTC datetime offset from now by the given duration."""
    delta = timedelta(days=days, hours=hours, minutes=minutes)
    return datetime.now(timezone.utc) - delta


def seed_repositories(ctx: RepositoryContext) -> None:
    """Populate all repositories with realistic development fixture data.

    Fixtures created:
    - 2 teams (Platform Team, Frontend Team)
    - 1 AdminConfig with a demo base issue URL
    - 3 sessions (2 Platform Team — 1 active, 1 completed; 1 Frontend Team — active)
    - 8 participants across the three sessions
    - 10 issues across the three sessions (several in various estimate states)
    - 2 hidden votes on the active issue in session-001

    Args:
        ctx: :class:`RepositoryContext` to populate; all stores are expected
             to be empty when this function is called.
    """

    # ------------------------------------------------------------------
    # Admin configuration
    # ------------------------------------------------------------------
    ctx.admin_config.save(
        AdminConfig(
            base_issue_url="https://jira.example.com/browse/",
            theme_default=ThemePreference.light,
            updated_at=_ago(days=30),
        )
    )

    # ------------------------------------------------------------------
    # Teams
    # ------------------------------------------------------------------
    platform_team = ctx.teams.create(
        Team(id="team-001", name="Platform Team", created_at=_ago(days=90), updated_at=_ago(days=90))
    )
    frontend_team = ctx.teams.create(
        Team(id="team-002", name="Frontend Team", created_at=_ago(days=90), updated_at=_ago(days=90))
    )

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------
    # session-001: Platform Team, Sprint 24, currently active
    session_001 = ctx.sessions.create(
        Session(
            id="session-001",
            team_id=platform_team.id,
            name="Sprint 24 Planning",
            sprint_number="24",
            card_set_id="cardset-default",
            status=SessionStatus.active,
            created_at=_ago(hours=2),
        )
    )

    # session-002: Platform Team, Sprint 23, completed 2 weeks ago
    session_002 = ctx.sessions.create(
        Session(
            id="session-002",
            team_id=platform_team.id,
            name="Sprint 23 Planning",
            sprint_number="23",
            card_set_id="cardset-default",
            status=SessionStatus.completed,
            created_at=_ago(days=14),
            completed_at=_ago(days=13, hours=22),
        )
    )

    # session-003: Frontend Team, Sprint 24, active
    session_003 = ctx.sessions.create(
        Session(
            id="session-003",
            team_id=frontend_team.id,
            name="Sprint 24 UI Sprint",
            sprint_number="24",
            card_set_id="cardset-default",
            status=SessionStatus.active,
            created_at=_ago(hours=1),
        )
    )

    # ------------------------------------------------------------------
    # Participants — session-001 (Platform Team / Sprint 24)
    # ------------------------------------------------------------------
    alice = ctx.participants.create(
        Participant(
            id="p-001",
            session_id=session_001.id,
            display_name="Alice Martin",
            initials="AM",
            is_leader=True,
            joined_at=_ago(hours=2),
        )
    )
    bob = ctx.participants.create(
        Participant(
            id="p-002",
            session_id=session_001.id,
            display_name="Bob Chen",
            initials="BC",
            joined_at=_ago(hours=2, minutes=1),
        )
    )
    carol = ctx.participants.create(
        Participant(
            id="p-003",
            session_id=session_001.id,
            display_name="Carol Diaz",
            initials="CD",
            joined_at=_ago(hours=1, minutes=55),
        )
    )

    # Wire leader and creator back onto the session
    session_001.leader_participant_id = alice.id
    session_001.created_by_participant_id = alice.id
    ctx.sessions.update(session_001)

    # ------------------------------------------------------------------
    # Participants — session-002 (Platform Team / Sprint 23, completed)
    # ------------------------------------------------------------------
    alice_s2 = ctx.participants.create(
        Participant(
            id="p-004",
            session_id=session_002.id,
            display_name="Alice Martin",
            initials="AM",
            is_leader=True,
            join_state=JoinState.left,
            joined_at=_ago(days=14),
        )
    )
    bob_s2 = ctx.participants.create(
        Participant(
            id="p-005",
            session_id=session_002.id,
            display_name="Bob Chen",
            initials="BC",
            join_state=JoinState.left,
            joined_at=_ago(days=14, minutes=2),
        )
    )
    session_002.leader_participant_id = alice_s2.id
    session_002.created_by_participant_id = alice_s2.id
    ctx.sessions.update(session_002)

    # ------------------------------------------------------------------
    # Participants — session-003 (Frontend Team / Sprint 24)
    # ------------------------------------------------------------------
    dave = ctx.participants.create(
        Participant(
            id="p-006",
            session_id=session_003.id,
            display_name="Dave Kim",
            initials="DK",
            is_leader=True,
            joined_at=_ago(hours=1),
        )
    )
    eve = ctx.participants.create(
        Participant(
            id="p-007",
            session_id=session_003.id,
            display_name="Eve Park",
            initials="EP",
            joined_at=_ago(minutes=58),
        )
    )
    session_003.leader_participant_id = dave.id
    session_003.created_by_participant_id = dave.id
    ctx.sessions.update(session_003)

    # ------------------------------------------------------------------
    # Issues — session-001
    # ------------------------------------------------------------------
    issue_001 = ctx.issues.create(
        Issue(
            id="issue-001",
            session_id=session_001.id,
            order_index=0,
            issue_type=IssueType.story,
            issue_key="AUTH-101",
            summary="As a user I can log in and access my dashboard",
            description=(
                "Implement the login page, credential validation, "
                "session token generation, and redirect to the user dashboard."
            ),
            is_active=True,
        )
    )
    ctx.issues.create(
        Issue(
            id="issue-002",
            session_id=session_001.id,
            order_index=1,
            issue_type=IssueType.story,
            issue_key="AUTH-102",
            summary="Password reset via email flow",
        )
    )
    ctx.issues.create(
        Issue(
            id="issue-003",
            session_id=session_001.id,
            order_index=2,
            issue_type=IssueType.bug,
            issue_key="AUTH-103",
            summary="Token refresh causes 401 on high-traffic endpoints",
            description="Intermittent 401 responses observed when multiple requests hit the refresh endpoint concurrently.",
        )
    )
    ctx.issues.create(
        Issue(
            id="issue-004",
            session_id=session_001.id,
            order_index=3,
            issue_type=IssueType.story,
            issue_key="AUTH-104",
            summary="OAuth 2.0 integration with Google sign-in",
        )
    )

    # ------------------------------------------------------------------
    # Issues — session-002 (completed, all finalized)
    # ------------------------------------------------------------------
    ctx.issues.create(
        Issue(
            id="issue-005",
            session_id=session_002.id,
            order_index=0,
            issue_type=IssueType.story,
            issue_key="DASH-001",
            summary="Dashboard overview metrics widget",
            final_estimate="5",
        )
    )
    ctx.issues.create(
        Issue(
            id="issue-006",
            session_id=session_002.id,
            order_index=1,
            issue_type=IssueType.story,
            issue_key="DASH-002",
            summary="User profile settings page",
            final_estimate="3",
        )
    )
    ctx.issues.create(
        Issue(
            id="issue-007",
            session_id=session_002.id,
            order_index=2,
            issue_type=IssueType.bug,
            issue_key="DASH-003",
            summary="Sidebar collapses unexpectedly on tablet viewport",
            final_estimate="2",
        )
    )

    # ------------------------------------------------------------------
    # Issues — session-003 (Frontend Team)
    # ------------------------------------------------------------------
    ctx.issues.create(
        Issue(
            id="issue-008",
            session_id=session_003.id,
            order_index=0,
            issue_type=IssueType.story,
            issue_key="UI-201",
            summary="Component library setup and Storybook baseline",
            is_active=True,
        )
    )
    ctx.issues.create(
        Issue(
            id="issue-009",
            session_id=session_003.id,
            order_index=1,
            issue_type=IssueType.bug,
            issue_key="UI-202",
            summary="Button focus ring missing in dark mode",
        )
    )
    ctx.issues.create(
        Issue(
            id="issue-010",
            session_id=session_003.id,
            order_index=2,
            issue_type=IssueType.story,
            issue_key="UI-203",
            summary="Responsive table component for data-heavy views",
        )
    )

    # ------------------------------------------------------------------
    # Votes — session-001, issue-001 (hidden, waiting for reveal)
    # ------------------------------------------------------------------
    ctx.votes.upsert(
        Vote(
            id="vote-001",
            session_id=session_001.id,
            issue_id=issue_001.id,
            participant_id=alice.id,
            selected_card="5",
            cast_at=_ago(minutes=10),
            updated_at=_ago(minutes=10),
        )
    )
    ctx.votes.upsert(
        Vote(
            id="vote-002",
            session_id=session_001.id,
            issue_id=issue_001.id,
            participant_id=bob.id,
            selected_card="8",
            cast_at=_ago(minutes=8),
            updated_at=_ago(minutes=8),
        )
    )
    # carol (p-003) has not voted yet — intentional gap to demo N/M count
    _ = carol  # suppress unused-variable lint warning
    _ = bob_s2
    _ = eve
