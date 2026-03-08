"""Contract tests for SCRUM Poker session creation and leadership transfer endpoints.

Requirement trace: OpenAPI contract — verifies HTTP response codes, content
types, and response body shapes for the US2 session lifecycle endpoints.
"""

from __future__ import annotations

import io
import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.services.session_service import SessionServiceError

# ── Shared test IDs ────────────────────────────────────────────────────────────

_TEAM_ID = str(uuid.uuid4())
_SESSION_ID = str(uuid.uuid4())
_PARTICIPANT_ID = str(uuid.uuid4())


# ── POST /api/v1/sessions ──────────────────────────────────────────────────────


class TestCreateSessionContract:
    """Contract tests for the create session endpoint."""

    def test_create_session_returns_201_with_session_detail_schema(self, client):
        """Successful session creation returns 201 with SessionDetail fields."""
        mock_session_detail = {
            "id": _SESSION_ID,
            "name": "Sprint 42",
            "team_id": _TEAM_ID,
            "sprint_number": 42,
            "status": "active",
            "card_set_name": "fibonacci_plus_specials",
            "created_at": "2026-03-08T10:00:00Z",
            "leader_participant_id": _PARTICIPANT_ID,
            "participants": [
                {
                    "id": _PARTICIPANT_ID,
                    "user_identifier": "creator@example.com",
                    "display_name": "Creator User",
                    "is_leader": True,
                    "joined_at": "2026-03-08T10:00:00Z",
                }
            ],
            "issues": [
                {
                    "id": str(uuid.uuid4()),
                    "issue_key": "PROJ-123",
                    "issue_type": "Story",
                    "summary": "Test issue",
                    "description": None,
                    "is_active": False,
                    "revealed_at": None,
                    "final_estimate": None,
                }
            ],
            "active_issue": None,
        }

        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_svc.create_session.return_value = mock_session_detail

        csv_content = b"Issue Type,Issue Key,Summary\nStory,PROJ-123,Test issue\n"
        csv_file = (io.BytesIO(csv_content), "issues.csv")

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.SessionService", return_value=mock_svc),
        ):
            resp = client.post(
                "/api/v1/sessions",
                data={
                    "team_id": _TEAM_ID,
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
        assert "application/json" in resp.content_type
        data = resp.get_json()
        assert "id" in data
        assert "name" in data
        assert "team_id" in data
        assert "sprint_number" in data
        assert "status" in data
        assert "card_set_name" in data
        assert "participants" in data
        assert "issues" in data
        assert "leader_participant_id" in data

    def test_create_session_with_invalid_csv_returns_400(self, client):
        """Session creation with invalid CSV returns 400 Bad Request."""
        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_svc.create_session.side_effect = SessionServiceError(
            "Missing required CSV columns: Issue Key", status_code=400
        )

        csv_content = b"Issue Type,Summary\nStory,Test issue\n"
        csv_file = (io.BytesIO(csv_content), "issues.csv")

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.SessionService", return_value=mock_svc),
        ):
            resp = client.post(
                "/api/v1/sessions",
                data={
                    "team_id": _TEAM_ID,
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

    def test_create_session_missing_required_fields_returns_400(self, client):
        """Session creation without required fields returns 400 Bad Request."""
        resp = client.post(
            "/api/v1/sessions",
            data={
                "team_id": _TEAM_ID,
                "sprint_number": "42",
            },
            content_type="multipart/form-data",
        )

        assert resp.status_code == 400

    def test_create_session_with_invalid_team_id_returns_400(self, client):
        """Session creation with invalid team_id UUID returns 400 Bad Request."""
        csv_content = b"Issue Type,Issue Key,Summary\nStory,PROJ-123,Test issue\n"
        csv_file = (io.BytesIO(csv_content), "issues.csv")

        resp = client.post(
            "/api/v1/sessions",
            data={
                "team_id": "not-a-uuid",
                "session_name": "Sprint 42",
                "sprint_number": "42",
                "card_set": "fibonacci_plus_specials",
                "issues_file": csv_file,
                "user_identifier": "creator@example.com",
            },
            content_type="multipart/form-data",
        )

        assert resp.status_code == 400


# ── POST /api/v1/sessions/{session_id}/leader ─────────────────────────────────


class TestTransferLeadershipContract:
    """Contract tests for the leadership transfer endpoint."""

    def test_transfer_leadership_returns_200_with_updated_session(self, client):
        """Successful leadership transfer returns 200 with updated SessionDetail."""
        new_leader_id = str(uuid.uuid4())
        mock_session_detail = {
            "id": _SESSION_ID,
            "name": "Sprint 42",
            "team_id": _TEAM_ID,
            "sprint_number": 42,
            "status": "active",
            "leader_participant_id": new_leader_id,
            "participants": [
                {
                    "id": _PARTICIPANT_ID,
                    "user_identifier": "creator@example.com",
                    "is_leader": False,
                },
                {
                    "id": new_leader_id,
                    "user_identifier": "new_leader@example.com",
                    "is_leader": True,
                },
            ],
        }

        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_svc.transfer_leadership.return_value = mock_session_detail

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.SessionService", return_value=mock_svc),
            patch(
                "app.routes.poker_api.RealtimeEventService.get_instance",
                return_value=MagicMock(),
            ),
        ):
            resp = client.post(
                f"/api/v1/sessions/{_SESSION_ID}/leader",
                json={
                    "current_leader_participant_id": _PARTICIPANT_ID,
                    "new_leader_participant_id": new_leader_id,
                },
            )

        assert resp.status_code == 200
        assert "application/json" in resp.content_type
        data = resp.get_json()
        assert "id" in data
        assert "leader_participant_id" in data
        assert data["leader_participant_id"] == new_leader_id

    def test_transfer_leadership_by_non_leader_returns_403(self, client):
        """Leadership transfer by non-leader returns 403 Forbidden."""
        new_leader_id = str(uuid.uuid4())
        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_svc.transfer_leadership.side_effect = SessionServiceError(
            "Only the current leader can transfer leadership.", status_code=403
        )

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.SessionService", return_value=mock_svc),
        ):
            resp = client.post(
                f"/api/v1/sessions/{_SESSION_ID}/leader",
                json={
                    "current_leader_participant_id": _PARTICIPANT_ID,
                    "new_leader_participant_id": new_leader_id,
                },
            )

        assert resp.status_code == 403

    def test_transfer_leadership_to_nonexistent_participant_returns_404(self, client):
        """Leadership transfer to non-existent participant returns 404 Not Found."""
        new_leader_id = str(uuid.uuid4())
        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_svc.transfer_leadership.side_effect = SessionServiceError(
            "New leader participant not found in session.", status_code=404
        )

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.SessionService", return_value=mock_svc),
        ):
            resp = client.post(
                f"/api/v1/sessions/{_SESSION_ID}/leader",
                json={
                    "current_leader_participant_id": _PARTICIPANT_ID,
                    "new_leader_participant_id": new_leader_id,
                },
            )

        assert resp.status_code == 404

    def test_transfer_leadership_missing_new_leader_id_returns_400(self, client):
        """Leadership transfer without new_leader_participant_id returns 400."""
        resp = client.post(
            f"/api/v1/sessions/{_SESSION_ID}/leader",
            json={"current_leader_participant_id": _PARTICIPANT_ID},
        )

        assert resp.status_code == 400

    def test_transfer_leadership_with_invalid_session_id_returns_400(self, client):
        """Leadership transfer with invalid session_id UUID returns 400."""
        new_leader_id = str(uuid.uuid4())
        resp = client.post(
            "/api/v1/sessions/not-a-uuid/leader",
            json={
                "current_leader_participant_id": _PARTICIPANT_ID,
                "new_leader_participant_id": new_leader_id,
            },
        )

        assert resp.status_code == 400


# ── GET /api/v1/sessions ───────────────────────────────────────────────────────


class TestListSessionsContract:
    """Contract tests for the list sessions endpoint."""

    def test_list_sessions_returns_200_with_array(self, client):
        """Successful session listing returns 200 with sessions array."""
        mock_sessions = [
            {
                "id": str(uuid.uuid4()),
                "name": "Sprint 42",
                "team_id": _TEAM_ID,
                "sprint_number": 42,
                "status": "active",
                "participant_count": 3,
                "updated_at": "2026-03-08T10:00:00Z",
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Sprint 41",
                "team_id": _TEAM_ID,
                "sprint_number": 41,
                "status": "completed",
                "participant_count": 5,
                "updated_at": "2026-03-07T10:00:00Z",
            },
        ]

        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_svc.list_sessions.return_value = mock_sessions

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.SessionService", return_value=mock_svc),
        ):
            resp = client.get("/api/v1/sessions")

        assert resp.status_code == 200
        assert "application/json" in resp.content_type
        data = resp.get_json()
        assert "sessions" in data
        assert isinstance(data["sessions"], list)
        assert len(data["sessions"]) == 2

    def test_list_sessions_with_filters_returns_200(self, client):
        """Session listing with query filters returns 200."""
        mock_sessions = [
            {
                "id": str(uuid.uuid4()),
                "name": "Sprint 42",
                "team_id": _TEAM_ID,
                "sprint_number": 42,
                "status": "active",
            }
        ]

        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_svc.list_sessions.return_value = mock_sessions

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.SessionService", return_value=mock_svc),
        ):
            resp = client.get(
                f"/api/v1/sessions?status=active&team_id={_TEAM_ID}&sprint_number=42"
            )

        assert resp.status_code == 200
