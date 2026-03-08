"""Realtime integration tests for vote count, reveal broadcast, and session lock.

Requirement trace:
- Two participants can cast votes; reveal returns the correct aggregate.
- Broadcast events are emitted after committed transactions (vote_cast,
  votes_revealed, session_completed).
- Voting is blocked (409) after issue reveal.
- Voting is blocked (409) after session completion.
"""

from __future__ import annotations

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


def _seed_session(db_session, n_participants: int = 2):
    """Create a session with team, active issue, and N participants.

    :param db_session: SQLAlchemy session to use for setup.
    :param n_participants: Number of participants to create.
    :returns: Tuple of (session, participants_list, issue).
    """
    team = Team(name=f"IntTeam-{uuid.uuid4().hex[:6]}")
    db_session.add(team)
    db_session.flush()

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

    return session, participants, issue


# ── Test classes ───────────────────────────────────────────────────────────────


class TestVoteCountAndReveal:
    """Integration tests for the full voting → reveal flow."""

    def test_two_participants_vote_and_reveal_returns_correct_aggregates(
        self, client, db_session, api_db_factory
    ):
        """Two votes followed by reveal returns all_votes_count==2 and correct average."""
        session, participants, issue = _seed_session(db_session, 2)
        session_id = str(session.id)
        issue_id = str(issue.id)

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
            # Participant 0 votes 5.
            resp = client.put(
                f"/api/v1/sessions/{session_id}/issues/{issue_id}/votes/me",
                json={
                    "participant_id": str(participants[0].id),
                    "card_value": "5",
                },
            )
            assert resp.status_code == 200

            # Participant 1 votes 8.
            resp = client.put(
                f"/api/v1/sessions/{session_id}/issues/{issue_id}/votes/me",
                json={
                    "participant_id": str(participants[1].id),
                    "card_value": "8",
                },
            )
            assert resp.status_code == 200

            # Reveal.
            resp = client.post(
                f"/api/v1/sessions/{session_id}/issues/{issue_id}/reveal"
            )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["all_votes_count"] == 2
        assert abs(data["average_numeric_vote"] - 6.5) < 0.001
        assert len(data["votes"]) == 2

        # Broadcast events should include vote_cast and votes_revealed.
        event_types = [e["type"] for e in broadcast_events]
        assert "vote_cast" in event_types
        assert "votes_revealed" in event_types

    def test_session_completed_broadcast_emitted(
        self, client, db_session, api_db_factory
    ):
        """Completing a session emits a session_completed broadcast event."""
        session, _, _ = _seed_session(db_session, 1)
        session_id = str(session.id)

        broadcast_events: list[dict] = []

        realtime = RealtimeEventService.get_instance()
        with (
            patch(
                "app.routes.poker_api.get_db_session",
                side_effect=api_db_factory,
            ),
            patch.object(
                realtime,
                "broadcast",
                side_effect=lambda s, e: broadcast_events.append(e),
            ),
        ):
            resp = client.post(f"/api/v1/sessions/{session_id}/complete")

        assert resp.status_code == 200
        assert any(e["type"] == "session_completed" for e in broadcast_events)


class TestPostRevealVoteLock:
    """Integration tests for post-reveal and post-completion voting blocks."""

    def test_vote_blocked_after_reveal_returns_409(
        self, client, db_session, api_db_factory
    ):
        """PUT vote after issue reveal returns 409 Conflict."""
        session, participants, issue = _seed_session(db_session, 1)
        session_id = str(session.id)
        issue_id = str(issue.id)

        realtime = RealtimeEventService.get_instance()
        with (
            patch(
                "app.routes.poker_api.get_db_session",
                side_effect=api_db_factory,
            ),
            patch.object(realtime, "broadcast"),
        ):
            # Reveal the issue first.
            client.post(f"/api/v1/sessions/{session_id}/issues/{issue_id}/reveal")

            # Attempt to vote after reveal.
            resp = client.put(
                f"/api/v1/sessions/{session_id}/issues/{issue_id}/votes/me",
                json={
                    "participant_id": str(participants[0].id),
                    "card_value": "3",
                },
            )

        assert resp.status_code == 409

    def test_vote_blocked_after_session_complete_returns_409(
        self, client, db_session, api_db_factory
    ):
        """PUT vote after session completion returns 409 Conflict."""
        session, participants, issue = _seed_session(db_session, 1)
        session_id = str(session.id)
        issue_id = str(issue.id)

        realtime = RealtimeEventService.get_instance()
        with (
            patch(
                "app.routes.poker_api.get_db_session",
                side_effect=api_db_factory,
            ),
            patch.object(realtime, "broadcast"),
        ):
            # Complete the session.
            client.post(f"/api/v1/sessions/{session_id}/complete")

            # Attempt to vote in a completed session.
            resp = client.put(
                f"/api/v1/sessions/{session_id}/issues/{issue_id}/votes/me",
                json={
                    "participant_id": str(participants[0].id),
                    "card_value": "5",
                },
            )

        assert resp.status_code == 409
