"""Repository for Vote entities."""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session as SASession

from app.models.vote import Vote


class VoteRepository:
    """Data access layer for Vote entities.

    :param db: Active SQLAlchemy database session.
    """

    def __init__(self, db: SASession) -> None:
        """Initialise with an open database session."""
        self._db = db

    def get_by_issue_and_participant(
        self, issue_id: uuid.UUID, participant_id: uuid.UUID
    ) -> Vote | None:
        """Fetch the current vote for an issue/participant pair.

        :param issue_id: UUID of the issue.
        :param participant_id: UUID of the participant.
        :returns: Matching Vote or ``None``.
        """
        stmt = select(Vote).where(
            Vote.issue_id == issue_id,
            Vote.participant_id == participant_id,
        )
        return self._db.scalars(stmt).first()

    def list_by_issue(self, issue_id: uuid.UUID) -> Sequence[Vote]:
        """Return all votes cast for a given issue.

        :param issue_id: UUID of the issue.
        :returns: Sequence of Vote records.
        """
        stmt = select(Vote).where(Vote.issue_id == issue_id)
        return self._db.scalars(stmt).all()

    def save(self, vote: Vote) -> Vote:
        """Persist a new or updated vote.

        :param vote: Vote instance to save.
        :returns: The saved Vote instance.
        """
        self._db.add(vote)
        self._db.flush()
        return vote

    def delete(self, vote: Vote) -> None:
        """Remove a vote record (vote withdrawal).

        :param vote: Vote instance to delete.
        """
        self._db.delete(vote)
        self._db.flush()
