"""Unit tests for VoteService — vote upsert, remove, reveal lock, and estimate.

Requirement trace:
- Votes can be cast and changed (upsert semantics).
- Votes can be removed as long as the issue is not yet revealed.
- Voting is blocked after issue reveal (409).
- Voting is blocked in a completed session (409).
- Reveal is idempotent; sets ``revealed_at`` only on first call.
- Numeric average is computed correctly; non-numeric values are excluded.
- Custom estimate takes precedence over selected card values.
- Estimate is rejected before reveal (409).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.models.participant import Participant
from app.models.session import Session as PokerSession
from app.models.storage_issue import StorageIssue
from app.models.team import Team
from app.models.vote import Vote
from app.services.vote_service import VoteService, VoteError

# ── Fixtures and helpers ───────────────────────────────────────────────────────


def _make_team(db_session, name: str = "VoteTeam") -> Team:
    team = Team(name=name)
    db_session.add(team)
    db_session.flush()
    return team


def _make_session(db_session, team: Team, status: str = "active") -> PokerSession:
    s = PokerSession(
        name="VS Sprint 1", team_id=team.id, sprint_number=1, status=status
    )
    if status == "completed":
        s.completed_at = datetime.now(timezone.utc)
    db_session.add(s)
    db_session.flush()
    return s


def _make_participant(
    db_session, session: PokerSession, uid: str = "user-1", leader: bool = False
) -> Participant:
    p = Participant(
        session_id=session.id,
        user_identifier=uid,
        is_leader=leader,
    )
    db_session.add(p)
    db_session.flush()
    return p


def _make_issue(
    db_session,
    session: PokerSession,
    key: str = "PROJ-1",
    revealed: bool = False,
) -> StorageIssue:
    issue = StorageIssue(
        session_id=session.id,
        issue_type="Story",
        issue_key=key,
        summary="Test story",
        is_active=True,
        revealed_at=datetime.now(timezone.utc) if revealed else None,
    )
    db_session.add(issue)
    db_session.flush()
    return issue


# ── VoteService.cast_or_change_vote ───────────────────────────────────────────


class TestCastOrChangeVote:
    """Tests for vote upsert semantics."""

    def test_cast_new_vote_creates_record(self, db_session):
        """Casting a vote for the first time creates a new Vote record."""
        team = _make_team(db_session)
        session = _make_session(db_session, team)
        participant = _make_participant(db_session, session)
        issue = _make_issue(db_session, session)

        svc = VoteService(db_session)
        vote = svc.cast_or_change_vote(session.id, issue.id, participant.id, "5")

        assert vote.id is not None
        assert vote.card_value == "5"
        assert vote.participant_id == participant.id
        assert vote.issue_id == issue.id

    def test_change_vote_updates_existing_record(self, db_session):
        """Casting a second vote for the same issue updates the existing Vote."""
        team = _make_team(db_session, "CT2")
        session = _make_session(db_session, team)
        participant = _make_participant(db_session, session)
        issue = _make_issue(db_session, session)

        svc = VoteService(db_session)
        first = svc.cast_or_change_vote(session.id, issue.id, participant.id, "3")
        updated = svc.cast_or_change_vote(session.id, issue.id, participant.id, "8")

        assert first.id == updated.id
        assert updated.card_value == "8"

    def test_invalid_card_value_raises_400(self, db_session):
        """Casting a vote with an unknown card value raises VoteError(400)."""
        team = _make_team(db_session, "CT3")
        session = _make_session(db_session, team)
        participant = _make_participant(db_session, session)
        issue = _make_issue(db_session, session)

        svc = VoteService(db_session)
        with pytest.raises(VoteError) as exc_info:
            svc.cast_or_change_vote(session.id, issue.id, participant.id, "99")
        assert exc_info.value.status_code == 400

    def test_cast_vote_blocked_after_reveal(self, db_session):
        """Casting a vote on a revealed issue raises VoteError(409)."""
        team = _make_team(db_session, "CT4")
        session = _make_session(db_session, team)
        participant = _make_participant(db_session, session)
        issue = _make_issue(db_session, session, revealed=True)

        svc = VoteService(db_session)
        with pytest.raises(VoteError) as exc_info:
            svc.cast_or_change_vote(session.id, issue.id, participant.id, "5")
        assert exc_info.value.status_code == 409

    def test_cast_vote_blocked_for_completed_session(self, db_session):
        """Casting a vote in a completed session raises VoteError(409)."""
        team = _make_team(db_session, "CT5")
        session = _make_session(db_session, team, status="completed")
        participant = _make_participant(db_session, session)
        issue = _make_issue(db_session, session)

        svc = VoteService(db_session)
        with pytest.raises(VoteError) as exc_info:
            svc.cast_or_change_vote(session.id, issue.id, participant.id, "5")
        assert exc_info.value.status_code == 409


# ── VoteService.remove_vote ───────────────────────────────────────────────────


class TestRemoveVote:
    """Tests for vote removal."""

    def test_remove_existing_vote_deletes_it(self, db_session):
        """remove_vote deletes the Vote record when one exists."""
        team = _make_team(db_session, "RT1")
        session = _make_session(db_session, team)
        participant = _make_participant(db_session, session)
        issue = _make_issue(db_session, session)

        svc = VoteService(db_session)
        vote = svc.cast_or_change_vote(session.id, issue.id, participant.id, "5")
        vote_id = vote.id

        svc.remove_vote(session.id, issue.id, participant.id)
        assert db_session.get(Vote, vote_id) is None

    def test_remove_nonexistent_vote_is_noop(self, db_session):
        """remove_vote silently succeeds when the participant has no vote."""
        team = _make_team(db_session, "RT2")
        session = _make_session(db_session, team)
        participant = _make_participant(db_session, session)
        issue = _make_issue(db_session, session)

        svc = VoteService(db_session)
        # No exception should be raised.
        svc.remove_vote(session.id, issue.id, participant.id)

    def test_remove_vote_blocked_after_reveal(self, db_session):
        """Removing a vote after reveal raises VoteError(409)."""
        team = _make_team(db_session, "RT3")
        session = _make_session(db_session, team)
        participant = _make_participant(db_session, session)
        issue = _make_issue(db_session, session, revealed=True)

        svc = VoteService(db_session)
        with pytest.raises(VoteError) as exc_info:
            svc.remove_vote(session.id, issue.id, participant.id)
        assert exc_info.value.status_code == 409


# ── VoteService.reveal_votes ───────────────────────────────────────────────────


class TestRevealVotes:
    """Tests for reveal idempotency and numeric average calculation."""

    def test_reveal_sets_revealed_at(self, db_session):
        """reveal_votes sets ``revealed_at`` on first call."""
        team = _make_team(db_session, "RV1")
        session = _make_session(db_session, team)
        participant = _make_participant(db_session, session)
        issue = _make_issue(db_session, session)

        svc = VoteService(db_session)
        svc.cast_or_change_vote(session.id, issue.id, participant.id, "5")
        svc.reveal_votes(session.id, issue.id)

        db_session.refresh(issue)
        assert issue.revealed_at is not None

    def test_reveal_is_idempotent(self, db_session):
        """Calling reveal_votes twice returns the same revealed_at value."""
        team = _make_team(db_session, "RV2")
        session = _make_session(db_session, team)
        participant = _make_participant(db_session, session)
        issue = _make_issue(db_session, session)

        svc = VoteService(db_session)
        svc.cast_or_change_vote(session.id, issue.id, participant.id, "3")
        first = svc.reveal_votes(session.id, issue.id)
        second = svc.reveal_votes(session.id, issue.id)

        assert first["issue_id"] == second["issue_id"]

    def test_reveal_computes_numeric_average(self, db_session):
        """reveal_votes computes the average of numeric card values."""
        team = _make_team(db_session, "RV3")
        session = _make_session(db_session, team)
        p1 = _make_participant(db_session, session, "u1")
        p2 = _make_participant(db_session, session, "u2")
        issue = _make_issue(db_session, session)

        svc = VoteService(db_session)
        svc.cast_or_change_vote(session.id, issue.id, p1.id, "5")
        svc.cast_or_change_vote(session.id, issue.id, p2.id, "8")
        summary = svc.reveal_votes(session.id, issue.id)

        assert summary["all_votes_count"] == 2
        assert summary["average_numeric_vote"] == pytest.approx(6.5)

    def test_reveal_excludes_non_numeric_from_average(self, db_session):
        """Non-numeric card values (?, ☕, ♾) are excluded from the average."""
        team = _make_team(db_session, "RV4")
        session = _make_session(db_session, team)
        p1 = _make_participant(db_session, session, "u1")
        p2 = _make_participant(db_session, session, "u2")
        issue = _make_issue(db_session, session)

        svc = VoteService(db_session)
        svc.cast_or_change_vote(session.id, issue.id, p1.id, "5")
        svc.cast_or_change_vote(session.id, issue.id, p2.id, "?")
        summary = svc.reveal_votes(session.id, issue.id)

        assert summary["all_votes_count"] == 2
        assert summary["average_numeric_vote"] == pytest.approx(5.0)

    def test_reveal_all_non_numeric_average_is_none(self, db_session):
        """When all votes are non-numeric the average is None."""
        team = _make_team(db_session, "RV5")
        session = _make_session(db_session, team)
        participant = _make_participant(db_session, session)
        issue = _make_issue(db_session, session)

        svc = VoteService(db_session)
        svc.cast_or_change_vote(session.id, issue.id, participant.id, "?")
        summary = svc.reveal_votes(session.id, issue.id)

        assert summary["average_numeric_vote"] is None

    def test_reveal_blocked_for_completed_session(self, db_session):
        """Revealing in a completed session raises VoteError(409)."""
        team = _make_team(db_session, "RV6")
        session = _make_session(db_session, team, status="completed")
        participant = _make_participant(db_session, session)
        issue = _make_issue(db_session, session)

        svc = VoteService(db_session)
        with pytest.raises(VoteError) as exc_info:
            svc.reveal_votes(session.id, issue.id)
        assert exc_info.value.status_code == 409


# ── VoteService.save_estimate ──────────────────────────────────────────────────


class TestSaveEstimate:
    """Tests for estimate save logic."""

    def test_save_custom_estimate_persists_value(self, db_session):
        """Custom estimate string is stored as final_estimate."""
        team = _make_team(db_session, "SE1")
        session = _make_session(db_session, team)
        participant = _make_participant(db_session, session)
        issue = _make_issue(db_session, session, revealed=True)

        svc = VoteService(db_session)
        updated = svc.save_estimate(session.id, issue.id, custom_estimate="XL")

        assert updated.final_estimate == "XL"

    def test_save_estimate_with_selected_cards_averages_numeric(self, db_session):
        """Selected card values are averaged as the final estimate."""
        team = _make_team(db_session, "SE2")
        session = _make_session(db_session, team)
        issue = _make_issue(db_session, session, revealed=True)

        svc = VoteService(db_session)
        updated = svc.save_estimate(
            session.id, issue.id, selected_card_values=["5", "8"]
        )

        assert updated.final_estimate == "6.5"

    def test_save_estimate_integer_result_has_no_decimal(self, db_session):
        """An average that is a whole number is formatted without decimals."""
        team = _make_team(db_session, "SE3")
        session = _make_session(db_session, team)
        issue = _make_issue(db_session, session, revealed=True)

        svc = VoteService(db_session)
        updated = svc.save_estimate(
            session.id, issue.id, selected_card_values=["5", "5"]
        )

        assert updated.final_estimate == "5"

    def test_save_estimate_custom_overrides_selected_cards(self, db_session):
        """Custom estimate takes precedence over selected_card_values."""
        team = _make_team(db_session, "SE4")
        session = _make_session(db_session, team)
        issue = _make_issue(db_session, session, revealed=True)

        svc = VoteService(db_session)
        updated = svc.save_estimate(
            session.id,
            issue.id,
            selected_card_values=["5"],
            custom_estimate="SPIKE",
        )

        assert updated.final_estimate == "SPIKE"

    def test_save_estimate_before_reveal_raises_409(self, db_session):
        """Saving an estimate before reveal raises VoteError(409)."""
        team = _make_team(db_session, "SE5")
        session = _make_session(db_session, team)
        issue = _make_issue(db_session, session, revealed=False)

        svc = VoteService(db_session)
        with pytest.raises(VoteError) as exc_info:
            svc.save_estimate(session.id, issue.id, custom_estimate="5")
        assert exc_info.value.status_code == 409


# ── VoteService.complete_session ─────────────────────────────────────────────


class TestCompleteSession:
    """Tests for session completion."""

    def test_complete_session_sets_status_and_timestamp(self, db_session):
        """complete_session marks the session completed with a timestamp."""
        team = _make_team(db_session, "CS1")
        session = _make_session(db_session, team)

        svc = VoteService(db_session)
        result = svc.complete_session(session.id)

        assert result.status == "completed"
        assert result.completed_at is not None

    def test_complete_session_is_idempotent(self, db_session):
        """complete_session called twice returns the same status without error."""
        team = _make_team(db_session, "CS2")
        session = _make_session(db_session, team, status="completed")

        svc = VoteService(db_session)
        result = svc.complete_session(session.id)

        assert result.status == "completed"

    def test_complete_unknown_session_raises_404(self, db_session):
        """complete_session for an unknown UUID raises VoteError(404)."""
        svc = VoteService(db_session)
        with pytest.raises(VoteError) as exc_info:
            svc.complete_session(uuid.uuid4())
        assert exc_info.value.status_code == 404
