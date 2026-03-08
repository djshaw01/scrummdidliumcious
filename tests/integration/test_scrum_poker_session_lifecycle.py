"""Integration tests for session creation flow and leadership transfer UI state.

Requirement trace:
- A user can create a session with CSV upload and is auto-assigned as leader.
- Issues are properly ingested from CSV with required column validation.
- Leadership can be transferred to another participant with appropriate state updates.
- Session listing returns sessions with participant counts and status.
"""

from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.models.participant import Participant
from app.models.session import Session as PokerSession
from app.models.storage_issue import StorageIssue
from app.models.team import Team
from app.services.realtime_event_service import RealtimeEventService

# ── Helpers ────────────────────────────────────────────────────────────────────


def _seed_team(db_session):
    """Create a team for testing.

    :param db_session: SQLAlchemy session to use for setup.
    :returns: Team model instance.
    """
    team = Team(name=f"IntTeam-{uuid.uuid4().hex[:6]}")
    db_session.add(team)
    db_session.flush()
    db_session.commit()
    return team


def _seed_session_with_participants(db_session, n_participants: int = 2):
    """Create a session with team and N participants.

    :param db_session: SQLAlchemy session to use for setup.
    :param n_participants: Number of participants to create.
    :returns: Tuple of (session, participants_list).
    """
    team = _seed_team(db_session)

    session = PokerSession(
        name="Integration Sprint",
        team_id=team.id,
        sprint_number=1,
    )
    db_session.add(session)
    db_session.flush()

    participants = []
    for i in range(n_participants):
        p = Participant(
            session_id=session.id,
            user_identifier=f"intuser-{i}",
            display_name=f"Int User {i}",
            is_leader=(i == 0),
        )
        db_session.add(p)
        participants.append(p)
    db_session.flush()

    session.leader_participant_id = participants[0].id

    issue = StorageIssue(
        session_id=session.id,
        issue_type="Story",
        issue_key="INT-1",
        summary="Integration test story",
        is_active=True,
    )
    db_session.add(issue)
    db_session.flush()
    db_session.commit()

    return session, participants


# ── Test classes ───────────────────────────────────────────────────────────────


class TestSessionCreation:
    """Integration tests for the full session creation flow with CSV upload."""

    def test_create_session_with_valid_csv_returns_session_with_issues(
        self, client, db_session, api_db_factory
    ):
        """Creating a session with valid CSV ingests issues and assigns creator as leader."""
        team = _seed_team(db_session)
        team_id = str(team.id)

        csv_content = (
            b"Issue Type,Issue Key,Summary,Description\n"
            b"Story,PROJ-123,First issue,First description\n"
            b"Bug,PROJ-124,Second issue,Second description\n"
        )
        csv_file = (io.BytesIO(csv_content), "issues.csv")

        broadcast_events: list[dict] = []

        def _make_db():
            return api_db_factory()

        def _capture_broadcast(sid, evt):
            broadcast_events.append(evt)

        realtime = RealtimeEventService.get_instance()
        with (
            patch("app.routes.poker_api.get_db_session", side_effect=_make_db),
            patch.object(realtime, "broadcast", side_effect=_capture_broadcast),
        ):
            resp = client.post(
                "/api/v1/sessions",
                data={
                    "team_id": team_id,
                    "session_name": "Sprint 42",
                    "sprint_number": "42",
                    "card_set": "fibonacci_plus_specials",
                    "issues_file": csv_file,
                    "user_identifier": "creator@example.com",
                    "display_name": "Creator User",
                },
                content_type="multipart/form-data",
            )

        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Sprint 42"
        assert data["sprint_number"] == 42
        assert data["status"] == "active"
        assert data["card_set_name"] == "fibonacci_plus_specials"
        assert len(data["issues"]) == 2
        assert data["issues"][0]["issue_key"] == "PROJ-123"
        assert data["issues"][1]["issue_key"] == "PROJ-124"
        assert len(data["participants"]) == 1
        assert data["participants"][0]["is_leader"] is True
        assert data["leader_participant_id"] == data["participants"][0]["id"]

    def test_create_session_with_missing_required_columns_returns_400(
        self, client, db_session, api_db_factory
    ):
        """Creating a session with missing CSV columns returns 400."""
        team = _seed_team(db_session)
        team_id = str(team.id)

        # Missing "Issue Key" column.
        csv_content = b"Issue Type,Summary\nStory,First issue\n"
        csv_file = (io.BytesIO(csv_content), "issues.csv")

        with patch(
            "app.routes.poker_api.get_db_session",
            side_effect=api_db_factory,
        ):
            resp = client.post(
                "/api/v1/sessions",
                data={
                    "team_id": team_id,
                    "session_name": "Sprint 42",
                    "sprint_number": "42",
                    "card_set": "fibonacci_plus_specials",
                    "issues_file": csv_file,
                    "user_identifier": "creator@example.com",
                },
                content_type="multipart/form-data",
            )

        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data
        assert "Issue Key" in data["error"]

    def test_create_session_with_extra_csv_columns_ignores_them(
        self, client, db_session, api_db_factory
    ):
        """Creating a session with extra CSV columns ignores unknown columns."""
        team = _seed_team(db_session)
        team_id = str(team.id)

        # Extra columns: Priority, Assignee.
        csv_content = (
            b"Issue Type,Issue Key,Summary,Priority,Assignee\n"
            b"Story,PROJ-123,First issue,High,Alice\n"
        )
        csv_file = (io.BytesIO(csv_content), "issues.csv")

        broadcast_events: list[dict] = []

        def _capture_broadcast(sid, evt):
            broadcast_events.append(evt)

        realtime = RealtimeEventService.get_instance()
        with (
            patch(
                "app.routes.poker_api.get_db_session",
                side_effect=api_db_factory,
            ),
            patch.object(realtime, "broadcast", side_effect=_capture_broadcast),
        ):
            resp = client.post(
                "/api/v1/sessions",
                data={
                    "team_id": team_id,
                    "session_name": "Sprint 42",
                    "sprint_number": "42",
                    "card_set": "fibonacci_plus_specials",
                    "issues_file": csv_file,
                    "user_identifier": "creator@example.com",
                },
                content_type="multipart/form-data",
            )

        assert resp.status_code == 201
        data = resp.get_json()
        assert len(data["issues"]) == 1
        assert data["issues"][0]["issue_key"] == "PROJ-123"


class TestLeadershipTransfer:
    """Integration tests for leadership transfer with UI state updates."""

    def test_transfer_leadership_from_creator_to_another_participant(
        self, client, db_session, api_db_factory
    ):
        """Leader can transfer leadership to another participant."""
        session, participants = _seed_session_with_participants(db_session, 3)
        session_id = str(session.id)
        leader_id = str(participants[0].id)
        new_leader_id = str(participants[1].id)

        broadcast_events: list[dict] = []

        def _make_db():
            return api_db_factory()

        def _capture_broadcast(sid, evt):
            broadcast_events.append(evt)

        realtime = RealtimeEventService.get_instance()
        with (
            patch("app.routes.poker_api.get_db_session", side_effect=_make_db),
            patch.object(realtime, "broadcast", side_effect=_capture_broadcast),
        ):
            resp = client.post(
                f"/api/v1/sessions/{session_id}/leader",
                json={
                    "current_leader_participant_id": leader_id,
                    "new_leader_participant_id": new_leader_id,
                },
            )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["leader_participant_id"] == new_leader_id

        # Verify leader flags in participants.
        participant_map = {p["id"]: p for p in data["participants"]}
        assert participant_map[leader_id]["is_leader"] is False
        assert participant_map[new_leader_id]["is_leader"] is True

        # Verify broadcast event emitted.
        event_types = [e["type"] for e in broadcast_events]
        assert "leadership_transferred" in event_types

    def test_transfer_leadership_by_non_leader_returns_403(
        self, client, db_session, api_db_factory
    ):
        """Non-leader participant cannot transfer leadership."""
        session, participants = _seed_session_with_participants(db_session, 3)
        session_id = str(session.id)
        non_leader_id = str(participants[1].id)
        new_leader_id = str(participants[2].id)

        with patch(
            "app.routes.poker_api.get_db_session",
            side_effect=api_db_factory,
        ):
            resp = client.post(
                f"/api/v1/sessions/{session_id}/leader",
                json={
                    "current_leader_participant_id": non_leader_id,
                    "new_leader_participant_id": new_leader_id,
                },
            )

        assert resp.status_code == 403

    def test_transfer_leadership_to_nonexistent_participant_returns_404(
        self, client, db_session, api_db_factory
    ):
        """Transferring leadership to non-existent participant returns 404."""
        session, participants = _seed_session_with_participants(db_session, 2)
        session_id = str(session.id)
        leader_id = str(participants[0].id)
        fake_participant_id = str(uuid.uuid4())

        with patch(
            "app.routes.poker_api.get_db_session",
            side_effect=api_db_factory,
        ):
            resp = client.post(
                f"/api/v1/sessions/{session_id}/leader",
                json={
                    "current_leader_participant_id": leader_id,
                    "new_leader_participant_id": fake_participant_id,
                },
            )

        assert resp.status_code == 404


class TestSessionListing:
    """Integration tests for session listing with filters."""

    def test_list_sessions_returns_all_sessions(
        self, client, db_session, api_db_factory
    ):
        """Listing sessions returns all sessions in reverse chronological order."""
        team = _seed_team(db_session)

        session1 = PokerSession(
            name="Sprint 41",
            team_id=team.id,
            sprint_number=41,
            status="completed",
        )
        session2 = PokerSession(
            name="Sprint 42",
            team_id=team.id,
            sprint_number=42,
            status="active",
        )
        db_session.add_all([session1, session2])
        db_session.commit()

        with patch(
            "app.routes.poker_api.get_db_session",
            side_effect=api_db_factory,
        ):
            resp = client.get("/api/v1/sessions")

        assert resp.status_code == 200
        data = resp.get_json()
        assert "sessions" in data
        assert len(data["sessions"]) == 2

        # Verify reverse chronological order (newest first).
        assert data["sessions"][0]["name"] == "Sprint 42"
        assert data["sessions"][1]["name"] == "Sprint 41"

    def test_list_sessions_filtered_by_status(self, client, db_session, api_db_factory):
        """Listing sessions with status filter returns only matching sessions."""
        team = _seed_team(db_session)

        session1 = PokerSession(
            name="Sprint 41",
            team_id=team.id,
            sprint_number=41,
            status="completed",
        )
        session2 = PokerSession(
            name="Sprint 42",
            team_id=team.id,
            sprint_number=42,
            status="active",
        )
        db_session.add_all([session1, session2])
        db_session.commit()

        with patch(
            "app.routes.poker_api.get_db_session",
            side_effect=api_db_factory,
        ):
            resp = client.get("/api/v1/sessions?status=active")

        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["status"] == "active"

    def test_list_sessions_filtered_by_team_id(
        self, client, db_session, api_db_factory
    ):
        """Listing sessions with team_id filter returns only matching sessions."""
        team1 = _seed_team(db_session)
        team2 = _seed_team(db_session)

        session1 = PokerSession(
            name="Team 1 Sprint",
            team_id=team1.id,
            sprint_number=1,
            status="active",
        )
        session2 = PokerSession(
            name="Team 2 Sprint",
            team_id=team2.id,
            sprint_number=1,
            status="active",
        )
        db_session.add_all([session1, session2])
        db_session.commit()

        with patch(
            "app.routes.poker_api.get_db_session",
            side_effect=api_db_factory,
        ):
            resp = client.get(f"/api/v1/sessions?team_id={str(team1.id)}")

        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["name"] == "Team 1 Sprint"
