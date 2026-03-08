"""Vote domain service — cast, change, remove, reveal, and estimate logic."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Sequence

from sqlalchemy.orm import Session as SASession

from app.models.session import Session as PokerSession
from app.models.storage_issue import StorageIssue
from app.models.vote import VALID_CARD_VALUES, Vote
from app.repositories.session_repository import SessionRepository
from app.repositories.vote_repository import VoteRepository


class VoteError(Exception):
    """Raised when a vote operation is not permitted.

    :param message: Human-readable error detail.
    :param status_code: Suggested HTTP status code for the API layer.
    """

    def __init__(self, message: str, status_code: int = 409) -> None:
        """Initialise with a message and HTTP status hint."""
        super().__init__(message)
        self.status_code = status_code


class VoteService:
    """Business logic for voting, reveal, and estimate operations.

    :param db: Active SQLAlchemy ORM session.
    """

    def __init__(self, db: SASession) -> None:
        """Initialise with an open database session."""
        self._db = db
        self._vote_repo = VoteRepository(db)
        self._session_repo = SessionRepository(db)

    def cast_or_change_vote(
        self,
        session_id: uuid.UUID,
        issue_id: uuid.UUID,
        participant_id: uuid.UUID,
        card_value: str,
    ) -> Vote:
        """Cast or change a participant's vote on an active issue.

        Performs an upsert: creates a new Vote when none exists for the
        ``(issue_id, participant_id)`` pair, or updates an existing one.

        :param session_id: UUID of the owning session.
        :param issue_id: UUID of the issue being voted on.
        :param participant_id: UUID of the voting participant.
        :param card_value: Selected card value from the allowed set.
        :returns: The persisted Vote record.
        :raises VoteError: If the card value is invalid, issue is revealed,
            or session is completed.
        """
        if card_value not in VALID_CARD_VALUES:
            raise VoteError(f"Invalid card value '{card_value}'.", status_code=400)
        self._assert_voting_open(session_id, issue_id)
        existing = self._vote_repo.get_by_issue_and_participant(
            issue_id, participant_id
        )
        if existing is not None:
            existing.card_value = card_value
            existing.updated_at = datetime.now(timezone.utc)
            self._db.flush()
            return existing
        vote = Vote(
            issue_id=issue_id,
            participant_id=participant_id,
            card_value=card_value,
        )
        return self._vote_repo.save(vote)

    def remove_vote(
        self,
        session_id: uuid.UUID,
        issue_id: uuid.UUID,
        participant_id: uuid.UUID,
    ) -> None:
        """Remove a participant's vote from an active issue.

        No-op if the participant has not yet cast a vote for the issue.

        :param session_id: UUID of the owning session.
        :param issue_id: UUID of the issue.
        :param participant_id: UUID of the participant withdrawing their vote.
        :raises VoteError: If the issue is revealed or session is completed.
        """
        self._assert_voting_open(session_id, issue_id)
        existing = self._vote_repo.get_by_issue_and_participant(
            issue_id, participant_id
        )
        if existing is not None:
            self._vote_repo.delete(existing)

    def reveal_votes(
        self,
        session_id: uuid.UUID,
        issue_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Reveal all votes for an issue with idempotent semantics.

        Sets ``revealed_at`` on the first successful call.  Subsequent calls
        return the existing reveal state without modifying the record.

        :param session_id: UUID of the owning session.
        :param issue_id: UUID of the issue to reveal.
        :returns: Dict matching the RevealedVoteSummary response schema.
        :raises VoteError: If the session is completed or the issue is not found.
        """
        session = self._get_session_or_raise(session_id)
        if session.status == "completed":
            raise VoteError("Session is completed.", status_code=409)
        issue = self._get_issue_or_raise(issue_id, session_id)
        if issue.revealed_at is None:
            issue.revealed_at = datetime.now(timezone.utc)
            self._db.flush()
        votes: Sequence[Vote] = self._vote_repo.list_by_issue(issue_id)
        total_participants = len(session.participants)
        return _build_reveal_summary(issue_id, votes, total_participants)

    def save_estimate(
        self,
        session_id: uuid.UUID,
        issue_id: uuid.UUID,
        *,
        selected_card_values: list[str] | None = None,
        custom_estimate: str | None = None,
    ) -> StorageIssue:
        """Save the final estimate for an issue after reveal.

        Custom estimate takes precedence over selected card values.  When
        ``selected_card_values`` contains numeric entries their average is
        computed and formatted as the estimate.  If neither argument is
        provided the issue record is returned unchanged.

        :param session_id: UUID of the owning session.
        :param issue_id: UUID of the issue to estimate.
        :param selected_card_values: Card values selected by the leader for
            averaging; non-numeric values are concatenated as-is.
        :param custom_estimate: Freeform estimate string typed by the leader.
        :returns: The updated StorageIssue record.
        :raises VoteError: If the issue has not been revealed yet.
        """
        issue = self._get_issue_or_raise(issue_id, session_id)
        if issue.revealed_at is None:
            raise VoteError(
                "Cannot save estimate before votes are revealed.", status_code=409
            )
        if custom_estimate is not None:
            stripped = custom_estimate.strip()
            issue.final_estimate = stripped if stripped else None
        elif selected_card_values:
            numeric = [float(v) for v in selected_card_values if _is_numeric(v)]
            if numeric:
                avg = sum(numeric) / len(numeric)
                issue.final_estimate = (
                    str(int(avg)) if avg == int(avg) else f"{avg:.1f}"
                )
            else:
                issue.final_estimate = ", ".join(selected_card_values)
        self._db.flush()
        return issue

    def complete_session(self, session_id: uuid.UUID) -> PokerSession:
        """Mark a session as completed, locking further voting.

        Idempotent — if the session is already completed its current state is
        returned without modification.

        :param session_id: UUID of the session to complete.
        :returns: The updated PokerSession record.
        :raises VoteError: If the session is not found.
        """
        session = self._get_session_or_raise(session_id)
        if session.status != "completed":
            session.status = "completed"
            session.completed_at = datetime.now(timezone.utc)
            self._db.flush()
        return session

    # ── Private helpers ────────────────────────────────────────────────────────

    def _assert_voting_open(self, session_id: uuid.UUID, issue_id: uuid.UUID) -> None:
        """Raise VoteError when voting is not permitted for the issue.

        Voting is blocked when the session is ``completed`` or when the issue
        has already been revealed.

        :param session_id: UUID of the session to check.
        :param issue_id: UUID of the issue to check.
        :raises VoteError: If voting is not currently permitted.
        """
        session = self._get_session_or_raise(session_id)
        if session.status == "completed":
            raise VoteError("Cannot vote in a completed session.", status_code=409)
        issue = self._get_issue_or_raise(issue_id, session_id)
        if issue.revealed_at is not None:
            raise VoteError("Cannot vote after issue reveal.", status_code=409)

    def _get_session_or_raise(self, session_id: uuid.UUID) -> PokerSession:
        """Return session by ID or raise VoteError with 404 status.

        :param session_id: UUID of the session to look up.
        :returns: Matching PokerSession.
        :raises VoteError: If no session is found.
        """
        session = self._session_repo.get_by_id(session_id)
        if session is None:
            raise VoteError(f"Session {session_id} not found.", status_code=404)
        return session

    def _get_issue_or_raise(
        self, issue_id: uuid.UUID, session_id: uuid.UUID
    ) -> StorageIssue:
        """Return issue by ID validating session ownership, or raise VoteError.

        :param issue_id: UUID of the issue to look up.
        :param session_id: UUID of the owning session (ownership check).
        :returns: Matching StorageIssue.
        :raises VoteError: If the issue is not found or belongs to a different
            session.
        """
        issue = self._db.get(StorageIssue, issue_id)
        if issue is None or issue.session_id != session_id:
            raise VoteError(f"Issue {issue_id} not found.", status_code=404)
        return issue


# ── Module-level helpers ───────────────────────────────────────────────────────


def _is_numeric(value: str) -> bool:
    """Return True when the card value can be parsed as a float.

    :param value: Card value string.
    :returns: Whether the value represents a numeric estimate.
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def _build_reveal_summary(
    issue_id: uuid.UUID,
    votes: Sequence[Vote],
    total_participants: int,
) -> dict[str, Any]:
    """Build the JSON-serialisable reveal summary dict.

    :param issue_id: UUID of the revealed issue.
    :param votes: Sequence of Vote records for the issue.
    :param total_participants: Total number of participants in the session.
    :returns: Dict matching the RevealedVoteSummary response schema.
    """
    vote_list = [
        {"participant_id": str(v.participant_id), "card_value": v.card_value}
        for v in votes
    ]
    numeric_values = [float(v.card_value) for v in votes if _is_numeric(v.card_value)]
    average = sum(numeric_values) / len(numeric_values) if numeric_values else None
    return {
        "issue_id": str(issue_id),
        "all_votes_count": len(vote_list),
        "total_participants": total_participants,
        "votes": vote_list,
        "average_numeric_vote": average,
    }
