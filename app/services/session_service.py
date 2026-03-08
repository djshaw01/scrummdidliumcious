"""Session domain service — issue activation, rejoin workflow, and session detail view."""

from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone
from typing import Any, TextIO

from sqlalchemy import select
from sqlalchemy.orm import Session as SASession

from app.models.participant import Participant
from app.models.session import Session as PokerSession
from app.models.storage_issue import StorageIssue
from app.models.team import Team
from app.repositories.session_repository import SessionRepository
from app.repositories.team_repository import TeamRepository
from app.services.csv_issue_import_service import (
    CSVIssueImportService,
    CSVValidationError,
)


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
        self._team_repo = TeamRepository(db)

    def create_session(
        self,
        team_id: uuid.UUID,
        session_name: str,
        sprint_number: int,
        card_set: str,
        issues_csv: TextIO,
        user_identifier: str,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        """Create a new session with CSV issue upload and auto-join creator as leader.

        This method:
        1. Validates the team exists.
        2. Parses and validates the CSV file.
        3. Creates a new session record.
        4. Creates issue records from CSV data.
        5. Creates a participant record for the creator.
        6. Assigns the creator as the session leader.
        7. Returns the full session detail.

        :param team_id: UUID of the team for this session.
        :param session_name: Display name for the session.
        :param sprint_number: Sprint number identifier.
        :param card_set: Card set name (e.g., "fibonacci_plus_specials").
        :param issues_csv: Text file object containing CSV data.
        :param user_identifier: User identifier for the creator.
        :param display_name: Optional display name for the creator.
        :returns: Session detail dict matching SessionDetail schema.
        :raises SessionServiceError: If validation fails or resources not found.
        """
        # Validate team exists.
        team = self._team_repo.get_by_id(team_id)
        if team is None:
            raise SessionServiceError(f"Team {team_id} not found.", status_code=404)

        # Parse and validate CSV.
        try:
            issues_data = CSVIssueImportService.parse_issues_csv(issues_csv)
        except CSVValidationError as exc:
            raise SessionServiceError(str(exc), status_code=400)

        # Create session record.
        session = PokerSession(
            name=session_name,
            team_id=team_id,
            sprint_number=sprint_number,
            card_set_name=card_set,
            status="active",
        )
        self._db.add(session)
        self._db.flush()

        # Create issue records.
        for issue_data in issues_data:
            issue = StorageIssue(
                session_id=session.id,
                issue_type=issue_data["issue_type"],
                issue_key=issue_data["issue_key"],
                summary=issue_data["summary"],
                description=issue_data.get("description"),
                is_active=False,
            )
            self._db.add(issue)

        # Create participant record for creator.
        creator = Participant(
            session_id=session.id,
            user_identifier=user_identifier,
            display_name=display_name,
            is_leader=True,
        )
        self._db.add(creator)
        self._db.flush()

        # Assign creator as leader.
        session.leader_participant_id = creator.id
        self._db.flush()
        self._db.commit()

        # Return session detail.
        return self._build_session_detail(session)

    def transfer_leadership(
        self,
        session_id: uuid.UUID,
        current_leader_participant_id: uuid.UUID,
        new_leader_participant_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Transfer session leadership from current leader to another participant.

        :param session_id: UUID of the session.
        :param current_leader_participant_id: UUID of the current leader.
        :param new_leader_participant_id: UUID of the new leader.
        :returns: Updated session detail dict.
        :raises SessionServiceError: If validation fails.
        """
        session = self._get_session_or_raise(session_id)

        # Verify current leader is actually the leader.
        current_leader = self._get_participant_or_raise(
            current_leader_participant_id, session_id
        )
        if not current_leader.is_leader:
            raise SessionServiceError(
                "Only the current leader can transfer leadership.", status_code=403
            )

        # Verify new leader exists in the session.
        new_leader = self._get_participant_or_raise(
            new_leader_participant_id, session_id
        )

        # Transfer leadership.
        current_leader.is_leader = False
        new_leader.is_leader = True
        session.leader_participant_id = new_leader.id
        self._db.flush()
        self._db.commit()

        # Return updated session detail.
        return self._build_session_detail(session)

    def list_sessions(
        self,
        status: str | None = None,
        team_id: uuid.UUID | None = None,
        sprint_number: int | None = None,
        name_query: str | None = None,
    ) -> list[dict[str, Any]]:
        """List sessions with optional filters in reverse chronological order.

        :param status: Filter by session status (active or completed).
        :param team_id: Filter by team UUID.
        :param sprint_number: Filter by exact sprint number.
        :param name_query: Filter by partial session name match (case-insensitive).
        :returns: List of session list item dicts.
        """
        # Build query with filters.
        stmt = select(PokerSession).order_by(PokerSession.created_at.desc())

        if status:
            stmt = stmt.where(PokerSession.status == status)
        if team_id:
            stmt = stmt.where(PokerSession.team_id == team_id)
        if sprint_number is not None:
            stmt = stmt.where(PokerSession.sprint_number == sprint_number)
        if name_query:
            stmt = stmt.where(PokerSession.name.ilike(f"%{name_query}%"))

        sessions = self._db.scalars(stmt).all()

        # Build session list items.
        return [
            {
                "id": str(s.id),
                "name": s.name,
                "team_id": str(s.team_id),
                "sprint_number": s.sprint_number,
                "status": s.status,
                "participant_count": len(s.participants),
                "updated_at": (
                    s.completed_at.isoformat()
                    if s.completed_at
                    else s.created_at.isoformat()
                ),
            }
            for s in sessions
        ]

    def get_last_session_name_for_team(self, team_id: uuid.UUID) -> str | None:
        """Get the most recent session name for a team.

        Used to prefill session name during new session creation.

        :param team_id: UUID of the team.
        :returns: Most recent session name or None if no sessions exist.
        """
        last_session = self._session_repo.get_most_recent_by_team(team_id)
        return last_session.name if last_session else None

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
        return self._build_session_detail(session)

    # ── Private helpers ────────────────────────────────────────────────────────

    def _build_session_detail(self, session: PokerSession) -> dict[str, Any]:
        """Build a SessionDetail response dict from a session instance.

        :param session: PokerSession instance.
        :returns: Dict matching the SessionDetail response schema.
        """
        active_issue: StorageIssue | None = next(
            (i for i in session.issues if i.is_active), None
        )
        return {
            "id": str(session.id),
            "name": session.name,
            "team_id": str(session.team_id),
            "team_name": session.team.name if session.team else None,
            "sprint_number": session.sprint_number,
            "status": session.status,
            "card_set_name": session.card_set_name,
            "created_at": session.created_at.isoformat(),
            "leader_participant_id": (
                str(session.leader_participant_id)
                if session.leader_participant_id
                else None
            ),
            "participants": [
                {
                    "id": str(p.id),
                    "user_identifier": p.user_identifier,
                    "display_name": p.display_name,
                    "is_leader": p.is_leader,
                    "joined_at": p.joined_at.isoformat(),
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
            "active_issue": (str(active_issue.id) if active_issue else None),
        }

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
