"""Session domain service — issue activation, rejoin workflow, and session detail view."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session as SASession

from app.models.participant import Participant
from app.models.session import Session as PokerSession
from app.models.storage_issue import StorageIssue
from app.repositories.session_repository import SessionRepository


class SessionServiceError(Exception):
    """Raised when a session operation cannot be completed.

    :param message: Human-readable error detail.
    :param status_code: Suggested HTTP status code for the API layer.
    """

    def __init__(self, message: str, status_code: int = 400) -> None:
        """Initialise with a message and HTTP status hint."""
        super().__init__(message)
        self.status_code = status_code


class SessionService:
    """Business logic for session navigation and participant management.

    :param db: Active SQLAlchemy ORM session.
    """

    def __init__(self, db: SASession) -> None:
        """Initialise with an open database session."""
        self._db = db
        self._session_repo = SessionRepository(db)

    def activate_issue(
        self,
        session_id: uuid.UUID,
        issue_id: uuid.UUID,
    ) -> StorageIssue:
        """Set the active issue for a session, deactivating any previous one.

        :param session_id: UUID of the session.
        :param issue_id: UUID of the issue to mark active.
        :returns: The newly active StorageIssue.
        :raises SessionServiceError: If the session or issue is not found.
        """
        session = self._get_session_or_raise(session_id)
        issue = self._get_issue_or_raise(issue_id, session_id)
        for existing in session.issues:
            if existing.is_active and existing.id != issue_id:
                existing.is_active = False
        issue.is_active = True
        self._db.flush()
        return issue

    def rejoin_active_issue(
        self,
        session_id: uuid.UUID,
        participant_id: uuid.UUID,
    ) -> StorageIssue | None:
        """Sync a participant's navigation pointer to the current active issue.

        Called when a participant navigated away and clicks the Rejoin button
        to jump back into the active voting flow.

        :param session_id: UUID of the session.
        :param participant_id: UUID of the participant rejoining.
        :returns: The current active StorageIssue, or ``None`` if none is active.
        :raises SessionServiceError: If the session or participant is not found.
        """
        session = self._get_session_or_raise(session_id)
        participant = self._get_participant_or_raise(participant_id, session_id)
        active_issue: StorageIssue | None = next(
            (i for i in session.issues if i.is_active), None
        )
        participant.active_issue_id = active_issue.id if active_issue else None
        self._db.flush()
        return active_issue

    def get_session_detail(self, session_id: uuid.UUID) -> dict[str, Any]:
        """Return a JSON-serialisable session detail dict.

        :param session_id: UUID of the session to describe.
        :returns: Dict matching the SessionDetail response schema.
        :raises SessionServiceError: If the session is not found.
        """
        session = self._get_session_or_raise(session_id)
        active_issue: StorageIssue | None = next(
            (i for i in session.issues if i.is_active), None
        )
        return {
            "session": {
                "id": str(session.id),
                "name": session.name,
                "sprint_number": session.sprint_number,
                "status": session.status,
                "team_name": session.team.name if session.team else None,
                "participant_count": len(session.participants),
                "created_at": session.created_at.isoformat(),
            },
            "participants": [
                {
                    "id": str(p.id),
                    "user_identifier": p.user_identifier,
                    "display_name": p.display_name,
                    "is_leader": p.is_leader,
                }
                for p in session.participants
            ],
            "issues": [
                {
                    "id": str(i.id),
                    "issue_key": i.issue_key,
                    "issue_type": i.issue_type,
                    "summary": i.summary,
                    "description": i.description,
                    "final_estimate": i.final_estimate,
                    "revealed_at": (
                        i.revealed_at.isoformat() if i.revealed_at else None
                    ),
                    "is_active": i.is_active,
                }
                for i in session.issues
            ],
            "active_issue_id": str(active_issue.id) if active_issue else None,
        }

    # ── Private helpers ────────────────────────────────────────────────────────

    def _get_session_or_raise(self, session_id: uuid.UUID) -> PokerSession:
        """Return session by ID or raise SessionServiceError with 404 status.

        :param session_id: UUID of the session to look up.
        :returns: Matching PokerSession.
        :raises SessionServiceError: If no session is found.
        """
        session = self._session_repo.get_by_id(session_id)
        if session is None:
            raise SessionServiceError(
                f"Session {session_id} not found.", status_code=404
            )
        return session

    def _get_issue_or_raise(
        self, issue_id: uuid.UUID, session_id: uuid.UUID
    ) -> StorageIssue:
        """Return issue by ID validating session ownership, or raise.

        :param issue_id: UUID of the issue to look up.
        :param session_id: UUID of the owning session.
        :returns: Matching StorageIssue.
        :raises SessionServiceError: If the issue is not found or belongs to a
            different session.
        """
        issue = self._db.get(StorageIssue, issue_id)
        if issue is None or issue.session_id != session_id:
            raise SessionServiceError(f"Issue {issue_id} not found.", status_code=404)
        return issue

    def _get_participant_or_raise(
        self, participant_id: uuid.UUID, session_id: uuid.UUID
    ) -> Participant:
        """Return participant by ID validating session ownership, or raise.

        :param participant_id: UUID of the participant to look up.
        :param session_id: UUID of the owning session.
        :returns: Matching Participant.
        :raises SessionServiceError: If the participant is not found or belongs
            to a different session.
        """
        participant = self._db.get(Participant, participant_id)
        if participant is None or participant.session_id != session_id:
            raise SessionServiceError(
                f"Participant {participant_id} not found.", status_code=404
            )
        return participant
