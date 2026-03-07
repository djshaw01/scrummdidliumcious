"""Repository for Team entities."""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session as SASession

from app.models.team import Team


class TeamRepository:
    """Data access layer for Team entities.

    :param db: Active SQLAlchemy database session.
    """

    def __init__(self, db: SASession) -> None:
        """Initialise with an open database session."""
        self._db = db

    def get_by_id(self, team_id: uuid.UUID) -> Team | None:
        """Fetch a team by primary key.

        :param team_id: UUID of the team to retrieve.
        :returns: Matching Team or ``None``.
        """
        return self._db.get(Team, team_id)

    def get_by_name(self, name: str) -> Team | None:
        """Fetch a team by name (case-insensitive).

        :param name: Team name to search.
        :returns: Matching Team or ``None``.
        """
        stmt = select(Team).where(Team.name.ilike(name))
        return self._db.scalars(stmt).first()

    def list_all(self) -> Sequence[Team]:
        """Return all teams ordered by name.

        :returns: Sequence of Team records.
        """
        stmt = select(Team).order_by(Team.name)
        return self._db.scalars(stmt).all()

    def save(self, team: Team) -> Team:
        """Persist a new or updated team.

        :param team: Team instance to save.
        :returns: The saved Team instance, flushed into the session.
        """
        self._db.add(team)
        self._db.flush()
        return team

    def delete(self, team: Team) -> None:
        """Delete a team record.

        :param team: Team instance to remove.
        """
        self._db.delete(team)
        self._db.flush()
