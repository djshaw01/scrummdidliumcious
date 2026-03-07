"""Pydantic DTO for vote cast and change requests."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, field_validator

#: Card values permitted by the fibonacci_plus_specials deck.
VALID_CARD_VALUES: frozenset[str] = frozenset(
    {"1", "2", "3", "5", "8", "13", "?", "\u2615", "\u267e"}
)


class VoteUpdateRequest(BaseModel):
    """Boundary model for casting or changing a vote on an issue.

    :param issue_id: UUID of the issue being voted on.
    :param participant_id: UUID of the voting participant.
    :param card_value: Selected card value from :data:`VALID_CARD_VALUES`.
    """

    issue_id: uuid.UUID
    participant_id: uuid.UUID
    card_value: str

    @field_validator("card_value")
    @classmethod
    def card_value_in_allowed_set(cls, v: str) -> str:
        """Validate that the chosen card value is in the allowed set.

        :param v: Candidate card value.
        :returns: Validated card value.
        :raises ValueError: If the value is not in the allowed set.
        """
        if v not in VALID_CARD_VALUES:
            allowed = ", ".join(sorted(VALID_CARD_VALUES))
            raise ValueError(
                f"card_value '{v}' is not valid. Allowed values: {allowed}"
            )
        return v
