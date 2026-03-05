"""Domain entities: Team, Session, Participant, Issue, Vote, VotingCardSet, AdminConfig."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


def _uid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def _now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class SessionStatus(str, Enum):
    """Lifecycle state of an estimation session."""

    active = "active"
    completed = "completed"


class JoinState(str, Enum):
    """Whether a participant is currently present in the session."""

    joined = "joined"
    left = "left"


class EvaluationState(str, Enum):
    """Whether a participant is engaged with the currently active issue."""

    active_issue_participating = "active_issue_participating"
    browsing_other_issue = "browsing_other_issue"


class IssueType(str, Enum):
    """Work-item type for an imported issue."""

    story = "Story"
    bug = "Bug"


class VisibilityState(str, Enum):
    """Vote visibility before and after the leader triggers reveal."""

    hidden = "hidden"
    revealed = "revealed"


class ThemePreference(str, Enum):
    """UI colour-scheme preference stored in AdminConfig."""

    light = "light"
    dark = "dark"


# ---------------------------------------------------------------------------
# Entities
# ---------------------------------------------------------------------------


@dataclass
class Team:
    """Named participant group used to scope sessions and name defaults.

    Args:
        name: Unique, non-empty display name for this team.
        id: UUID string (auto-generated when omitted).
        is_active: Whether the team is available for new session setup.
        created_at: UTC timestamp of creation.
        updated_at: UTC timestamp of last modification.
    """

    name: str
    id: str = field(default_factory=_uid)
    is_active: bool = True
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


@dataclass
class VotingCardSet:
    """Ordered set of card values available for voting in a session.

    Args:
        name: Display name for this card set.
        cards: Ordered list of card value strings.
        id: UUID string (auto-generated when omitted).
        created_at: UTC timestamp of creation.
    """

    name: str
    cards: list[str]
    id: str = field(default_factory=_uid)
    created_at: datetime = field(default_factory=_now)

    @staticmethod
    def make_default() -> VotingCardSet:
        """Return the canonical default Fibonacci-extended card set."""
        return VotingCardSet(
            id="cardset-default",
            name="Fibonacci Extended",
            cards=["1", "2", "3", "5", "8", "13", "?", "☕️", "♾️"],
        )


@dataclass
class AdminConfig:
    """Singleton workspace-level configuration used by session UX.

    Args:
        id: Fixed singleton key — always ``"config"``.
        base_issue_url: URL prefix used to build issue links from imported keys.
            ``None`` means issue keys render as non-clickable.
        theme_default: Default UI theme applied to new visitors.
        updated_at: UTC timestamp of last modification.
    """

    id: str = "config"
    base_issue_url: Optional[str] = None
    theme_default: ThemePreference = ThemePreference.light
    updated_at: datetime = field(default_factory=_now)


@dataclass
class Session:
    """Time-bound estimation event tied to one team.

    Args:
        team_id: FK reference to a :class:`Team`.
        name: Human-readable session title.
        sprint_number: Sprint identifier string (e.g. ``"24"``).
        card_set_id: FK reference to the :class:`VotingCardSet` in use.
        id: UUID string (auto-generated when omitted).
        status: Current lifecycle state — ``active`` or ``completed``.
        leader_participant_id: FK reference to the current session leader
            :class:`Participant`. Required while the session is active.
        created_by_participant_id: FK reference to the initiating participant.
        created_at: UTC timestamp of creation.
        completed_at: UTC timestamp when the session was completed, or ``None``.
    """

    team_id: str
    name: str
    sprint_number: str
    card_set_id: str
    id: str = field(default_factory=_uid)
    status: SessionStatus = SessionStatus.active
    leader_participant_id: Optional[str] = None
    created_by_participant_id: Optional[str] = None
    created_at: datetime = field(default_factory=_now)
    completed_at: Optional[datetime] = None


@dataclass
class Participant:
    """User presence and role record within a session.

    Args:
        session_id: FK reference to the parent :class:`Session`.
        display_name: Full display name of the participant.
        initials: Short initials string rendered in participant icons.
        id: UUID string (auto-generated when omitted).
        is_leader: Whether this participant currently leads the session.
        join_state: Connection state — ``joined`` or ``left``.
        evaluation_state: Whether the participant is engaging with the active
            issue or browsing a different issue.
        joined_at: UTC timestamp of session join.
        left_at: UTC timestamp when the participant left, or ``None``.
    """

    session_id: str
    display_name: str
    initials: str
    id: str = field(default_factory=_uid)
    is_leader: bool = False
    join_state: JoinState = JoinState.joined
    evaluation_state: EvaluationState = EvaluationState.active_issue_participating
    joined_at: datetime = field(default_factory=_now)
    left_at: Optional[datetime] = None


@dataclass
class Issue:
    """Imported work item to be estimated within a session.

    Args:
        session_id: FK reference to the parent :class:`Session`.
        order_index: Zero-based display order in the navigation column.
        issue_type: Work-item type — ``Story`` or ``Bug``.
        issue_key: Identifier string from the issue tracker (e.g. ``"AUTH-101"``).
        summary: One-line issue title.
        id: UUID string (auto-generated when omitted).
        description: Optional multi-paragraph description body.
        prior_estimate: Optional estimate from a previous planning session.
        final_estimate: Final leader-selected or custom estimate string, or ``None``.
        is_active: Whether this issue is currently selected for evaluation.
        revealed_at: UTC timestamp of vote reveal, or ``None`` if not yet revealed.
    """

    session_id: str
    order_index: int
    issue_type: IssueType
    issue_key: str
    summary: str
    id: str = field(default_factory=_uid)
    description: Optional[str] = None
    prior_estimate: Optional[str] = None
    final_estimate: Optional[str] = None
    is_active: bool = False
    revealed_at: Optional[datetime] = None


@dataclass
class Vote:
    """Participant card selection for the currently active issue.

    Args:
        session_id: FK reference to the parent :class:`Session`.
        issue_id: FK reference to the :class:`Issue` being voted on.
        participant_id: FK reference to the voting :class:`Participant`.
        selected_card: Card value string from the session card set.
        id: UUID string (auto-generated when omitted).
        visibility_state: ``hidden`` until the leader triggers reveal.
        cast_at: UTC timestamp of initial vote submission.
        updated_at: UTC timestamp of last card change.
    """

    session_id: str
    issue_id: str
    participant_id: str
    selected_card: str
    id: str = field(default_factory=_uid)
    visibility_state: VisibilityState = VisibilityState.hidden
    cast_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


__all__ = [
    "AdminConfig",
    "EvaluationState",
    "Issue",
    "IssueType",
    "JoinState",
    "Participant",
    "Session",
    "SessionStatus",
    "Team",
    "ThemePreference",
    "VisibilityState",
    "Vote",
    "VotingCardSet",
]

