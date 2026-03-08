"""Repository for Session entities."""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session as SASession

from app.models.session import Session as PokerSession


class SessionRepository:
    """Data access layer for PokerSession entities.

    :param db: Active SQLAlchemy database session.
    """

    def __init__(self, db: SASession) -> None:
        """Initialise with an open database session."""
        self._db = db

    def get_by_id(self, session_id: uuid.UUID) -> PokerSession | None:
        """Fetch a session by primary key.

        :param session_id: UUID of the session to retrieve.
        :returns: Matching session or ``None``.
        """
        return self._db.get(PokerSession, session_id)

    def list_active(self) -> Sequence[PokerSession]:
        """Return all sessions with status ``active``.

        :returns: Sequence of active session records.
        """
        stmt = select(PokerSession).where(PokerSession.status == "active")
        return self._db.scalars(stmt).all()

    def list_all(self) -> Sequence[PokerSession]:
        """Return all sessions ordered by created_at descending.

        :returns: Sequence of all session records, newest first.
        """
        stmt = select(PokerSession).order_by(PokerSession.created_at.desc())
        return self._db.scalars(stmt).all()

    def list_by_team(self, team_id: uuid.UUID) -> Sequence[PokerSession]:
        """Return all sessions for a given team, newest first.

        :param team_id: UUID of the team to filter by.
        :returns: Sequence of matching session records.
        """
        stmt = (
            select(PokerSession)
            .where(PokerSession.team_id == team_id)
            .order_by(PokerSession.created_at.desc())
        )
        return self._db.scalars(stmt).all()

    def get_most_recent_by_team(self, team_id: uuid.UUID) -> PokerSession | None:
        """Fetch the most recent session for a team.

        Used to prefill session name during new session creation.

        :param team_id: UUID of the team.
        :returns: Most recent PokerSession or None if no sessions exist.
        """
        stmt = (
            select(PokerSession)
            .where(PokerSession.team_id == team_id)
            .order_by(PokerSession.created_at.desc())
            .limit(1)
        )
        return self._db.scalars(stmt).first()

    def save(self, session: PokerSession) -> PokerSession:
        """Persist a new or updated session.

        :param session: PokerSession instance to save.
        :returns: The saved instance, flushed into the SA session.
        """
        self._db.add(session)
        self._db.flush()
        return session

    def delete(self, session: PokerSession) -> None:
        """Delete a session record.

        :param session: PokerSession instance to remove.
        """
        self._db.delete(session)
        self._db.flush()
