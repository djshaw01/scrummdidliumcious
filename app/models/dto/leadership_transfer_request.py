"""Pydantic DTO for session leadership transfer requests."""

from __future__ import annotations

import uuid

from pydantic import BaseModel


class LeadershipTransferRequest(BaseModel):
    """Boundary model for transferring session leadership to another participant.

    :param session_id: UUID of the session in which leadership is being transferred.
    :param new_leader_participant_id: UUID of the participant to designate as new leader.
    """

    session_id: uuid.UUID
    new_leader_participant_id: uuid.UUID
