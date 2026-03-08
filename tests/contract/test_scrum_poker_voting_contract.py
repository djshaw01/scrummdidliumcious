"""Contract tests for SCRUM Poker voting, reveal, estimate, and session-complete endpoints.

Requirement trace: OpenAPI contract — verifies HTTP response codes, content
types, and response body shapes for the US1 voting lifecycle endpoints.
"""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.services.vote_service import VoteError

# ── Shared test IDs ────────────────────────────────────────────────────────────

_SESSION_ID = str(uuid.uuid4())
_ISSUE_ID = str(uuid.uuid4())
_PARTICIPANT_ID = str(uuid.uuid4())


# ── POST /api/v1/sessions/{session_id}/issues/{issue_id}/reveal ───────────────


class TestRevealContract:
    """Contract tests for the reveal-votes endpoint."""

    def test_reveal_returns_200_with_summary_schema(self, client):
        """Successful reveal returns 200 with RevealedVoteSummary fields."""
        mock_summary = {
            "issue_id": _ISSUE_ID,
            "all_votes_count": 2,
            "total_participants": 3,
            "votes": [
                {"participant_id": str(uuid.uuid4()), "card_value": "5"},
                {"participant_id": str(uuid.uuid4()), "card_value": "8"},
            ],
            "average_numeric_vote": 6.5,
        }
        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_svc.reveal_votes.return_value = mock_summary

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.VoteService", return_value=mock_svc),
            patch(
                "app.routes.poker_api.RealtimeEventService.get_instance",
                return_value=MagicMock(),
            ),
        ):
            resp = client.post(
                f"/api/v1/sessions/{_SESSION_ID}/issues/{_ISSUE_ID}/reveal"
            )

        assert resp.status_code == 200
        assert "application/json" in resp.content_type
        data = resp.get_json()
        assert "issue_id" in data
        assert "all_votes_count" in data
        assert "votes" in data
        assert "average_numeric_vote" in data

    def test_reveal_on_completed_session_returns_409(self, client):
        """Reveal on a completed session returns 409 Conflict."""
        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_svc.reveal_votes.side_effect = VoteError(
            "Session is completed.", status_code=409
        )

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.VoteService", return_value=mock_svc),
        ):
            resp = client.post(
                f"/api/v1/sessions/{_SESSION_ID}/issues/{_ISSUE_ID}/reveal"
            )

        assert resp.status_code == 409


# ── PUT /api/v1/sessions/{session_id}/issues/{issue_id}/votes/me ──────────────


class TestUpsertVoteContract:
    """Contract tests for the cast-or-change-vote endpoint."""

    def test_upsert_vote_returns_200_with_vote_schema(self, client):
        """Valid vote upsert returns 200 with id and card_value."""
        vote_id = str(uuid.uuid4())
        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_vote = MagicMock()
        mock_vote.id = uuid.UUID(vote_id)
        mock_vote.card_value = "5"
        mock_svc.cast_or_change_vote.return_value = mock_vote
        mock_svc._vote_repo.list_by_issue.return_value = [mock_vote]

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.VoteService", return_value=mock_svc),
            patch(
                "app.routes.poker_api.RealtimeEventService.get_instance",
                return_value=MagicMock(),
            ),
        ):
            resp = client.put(
                f"/api/v1/sessions/{_SESSION_ID}/issues/{_ISSUE_ID}/votes/me",
                json={"participant_id": _PARTICIPANT_ID, "card_value": "5"},
            )

        assert resp.status_code == 200
        data = resp.get_json()
        assert "id" in data
        assert "card_value" in data
        assert data["card_value"] == "5"

    def test_upsert_vote_after_reveal_returns_409(self, client):
        """Voting on a revealed issue returns 409 Conflict."""
        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_svc.cast_or_change_vote.side_effect = VoteError(
            "Cannot vote after issue reveal.", status_code=409
        )

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.VoteService", return_value=mock_svc),
        ):
            resp = client.put(
                f"/api/v1/sessions/{_SESSION_ID}/issues/{_ISSUE_ID}/votes/me",
                json={"participant_id": _PARTICIPANT_ID, "card_value": "5"},
            )

        assert resp.status_code == 409

    def test_upsert_vote_missing_participant_id_returns_400(self, client):
        """PUT without participant_id returns 400 Bad Request."""
        resp = client.put(
            f"/api/v1/sessions/{_SESSION_ID}/issues/{_ISSUE_ID}/votes/me",
            json={"card_value": "5"},
        )
        assert resp.status_code == 400

    def test_upsert_vote_missing_card_value_returns_400(self, client):
        """PUT without card_value returns 400 Bad Request."""
        resp = client.put(
            f"/api/v1/sessions/{_SESSION_ID}/issues/{_ISSUE_ID}/votes/me",
            json={"participant_id": _PARTICIPANT_ID},
        )
        assert resp.status_code == 400


# ── DELETE /api/v1/sessions/{session_id}/issues/{issue_id}/votes/me ──────────


class TestDeleteVoteContract:
    """Contract tests for the remove-vote endpoint."""

    def test_delete_vote_returns_204(self, client):
        """Valid delete returns 204 No Content."""
        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_svc.remove_vote.return_value = None
        mock_svc._vote_repo.list_by_issue.return_value = []

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.VoteService", return_value=mock_svc),
            patch(
                "app.routes.poker_api.RealtimeEventService.get_instance",
                return_value=MagicMock(),
            ),
        ):
            resp = client.delete(
                f"/api/v1/sessions/{_SESSION_ID}/issues/{_ISSUE_ID}/votes/me"
                f"?participant_id={_PARTICIPANT_ID}"
            )

        assert resp.status_code == 204

    def test_delete_vote_missing_participant_id_returns_400(self, client):
        """DELETE without participant_id query param returns 400."""
        resp = client.delete(
            f"/api/v1/sessions/{_SESSION_ID}/issues/{_ISSUE_ID}/votes/me"
        )
        assert resp.status_code == 400


# ── POST /api/v1/sessions/{session_id}/issues/{issue_id}/estimate ─────────────


class TestSaveEstimateContract:
    """Contract tests for the save-estimate endpoint."""

    def test_save_estimate_returns_200_with_estimate_schema(self, client):
        """Valid estimate save returns 200 with issue_id and final_estimate."""
        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_issue = MagicMock()
        mock_issue.id = uuid.UUID(_ISSUE_ID)
        mock_issue.final_estimate = "8"
        mock_svc.save_estimate.return_value = mock_issue

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.VoteService", return_value=mock_svc),
            patch(
                "app.routes.poker_api.RealtimeEventService.get_instance",
                return_value=MagicMock(),
            ),
        ):
            resp = client.post(
                f"/api/v1/sessions/{_SESSION_ID}/issues/{_ISSUE_ID}/estimate",
                json={"custom_estimate": "8"},
            )

        assert resp.status_code == 200
        data = resp.get_json()
        assert "issue_id" in data
        assert "final_estimate" in data

    def test_save_estimate_before_reveal_returns_409(self, client):
        """Saving estimate before reveal returns 409 Conflict."""
        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_svc.save_estimate.side_effect = VoteError(
            "Cannot save estimate before votes are revealed.", status_code=409
        )

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.VoteService", return_value=mock_svc),
        ):
            resp = client.post(
                f"/api/v1/sessions/{_SESSION_ID}/issues/{_ISSUE_ID}/estimate",
                json={"custom_estimate": "5"},
            )

        assert resp.status_code == 409


# ── POST /api/v1/sessions/{session_id}/complete ───────────────────────────────


class TestCompleteSessionContract:
    """Contract tests for the complete-session endpoint."""

    def test_complete_session_returns_200_with_status_schema(self, client):
        """Completing a session returns 200 with session_id and status."""
        mock_db = MagicMock()
        mock_svc = MagicMock()
        mock_session = MagicMock()
        mock_session.id = uuid.UUID(_SESSION_ID)
        mock_session.status = "completed"
        mock_svc.complete_session.return_value = mock_session

        with (
            patch("app.routes.poker_api.get_db_session", return_value=mock_db),
            patch("app.routes.poker_api.VoteService", return_value=mock_svc),
            patch(
                "app.routes.poker_api.RealtimeEventService.get_instance",
                return_value=MagicMock(),
            ),
        ):
            resp = client.post(f"/api/v1/sessions/{_SESSION_ID}/complete")

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "completed"
        assert "session_id" in data

    def test_complete_session_invalid_uuid_returns_400(self, client):
        """Malformed session_id in URL returns 400 Bad Request."""
        resp = client.post("/api/v1/sessions/not-a-uuid/complete")
        assert resp.status_code == 400
