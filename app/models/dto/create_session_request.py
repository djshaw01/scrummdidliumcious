"""Pydantic DTO for new session creation requests."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, field_validator


class CreateSessionRequest(BaseModel):
    """Boundary model for creating a new SCRUM Poker session.

    :param name: Session display name (non-blank, stripped).
    :param team_id: UUID of the team that owns this session.
    :param sprint_number: Sprint iteration number (must be a positive integer).
    :param card_set_name: Estimation card set to use (default ``fibonacci_plus_specials``).
    :param user_identifier: Identity string of the session creator; auto-joined as leader.
    :param display_name: Optional human-readable name for the creator participant.
    """

    name: str
    team_id: uuid.UUID
    sprint_number: int
    card_set_name: str = "fibonacci_plus_specials"
    user_identifier: str
    display_name: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        """Reject blank or whitespace-only session names.

        :param v: Candidate session name.
        :returns: Stripped session name.
        :raises ValueError: If the name is blank after stripping.
        """
        if not v.strip():
            raise ValueError("Session name must not be blank.")
        return v.strip()

    @field_validator("sprint_number")
    @classmethod
    def sprint_number_positive(cls, v: int) -> int:
        """Enforce a positive sprint number.

        :param v: Candidate sprint number.
        :returns: Validated sprint number.
        :raises ValueError: If the value is not positive.
        """
        if v <= 0:
            raise ValueError("sprint_number must be a positive integer.")
        return v

    @field_validator("user_identifier")
    @classmethod
    def user_identifier_not_blank(cls, v: str) -> str:
        """Reject blank user identifiers.

        :param v: Candidate user identifier.
        :returns: Stripped user identifier.
        :raises ValueError: If the identifier is blank after stripping.
        """
        if not v.strip():
            raise ValueError("user_identifier must not be blank.")
        return v.strip()
