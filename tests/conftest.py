"""Shared pytest fixtures for session, issue, and participant test data."""

from datetime import datetime, timezone

import pytest

from app.domain.entities.issue import Issue
from app.domain.entities.participant import Participant
from app.domain.entities.session import Session


@pytest.fixture
def sample_session() -> Session:
    """Return a canonical active session fixture.

    Returns:
        Session fixture instance.
    """
    now = datetime.now(timezone.utc)
    return Session(
        id="session-1",
        team_id="team-platform",
        name="Sprint Planning",
        sprint_number="42",
        card_set_id="default-fibonacci",
        status="active",
        leader_participant_id="participant-a",
        created_by_participant_id="participant-a",
        created_at=now,
    )


@pytest.fixture
def sample_participants() -> list[Participant]:
    """Return a small participant list fixture.

    Returns:
        List of Participant entities.
    """
    now = datetime.now(timezone.utc)
    return [
        Participant(
            id="participant-a",
            session_id="session-1",
            display_name="Alex",
            initials="AL",
            is_leader=True,
            join_state="joined",
            evaluation_state="active_issue_participating",
            joined_at=now,
        ),
        Participant(
            id="participant-b",
            session_id="session-1",
            display_name="Blair",
            initials="BL",
            is_leader=False,
            join_state="joined",
            evaluation_state="active_issue_participating",
            joined_at=now,
        ),
    ]


@pytest.fixture
def sample_issues() -> list[Issue]:
    """Return ordered issue fixtures for one session.

    Returns:
        List of Issue entities.
    """
    return [
        Issue(
            id="issue-1",
            session_id="session-1",
            order_index=1,
            issue_type="Story",
            issue_key="APP-101",
            summary="Implement login flow",
            description="",
            prior_estimate="3",
            final_estimate=None,
            is_active=True,
        ),
        Issue(
            id="issue-2",
            session_id="session-1",
            order_index=2,
            issue_type="Bug",
            issue_key="APP-102",
            summary="Fix websocket reconnect",
            description="",
            prior_estimate=None,
            final_estimate=None,
            is_active=False,
        ),
    ]
