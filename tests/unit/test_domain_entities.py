"""Unit tests for domain entity construction and default values."""

from datetime import datetime, timezone

from app.domain.entities import (
    AdminConfig,
    EvaluationState,
    Issue,
    IssueType,
    JoinState,
    Participant,
    Session,
    SessionStatus,
    Team,
    ThemePreference,
    VisibilityState,
    Vote,
    VotingCardSet,
)


class TestTeam:
    def test_required_fields(self):
        team = Team(name="Acme Squad")
        assert team.name == "Acme Squad"
        assert team.is_active is True
        assert isinstance(team.id, str) and len(team.id) == 36
        assert isinstance(team.created_at, datetime)

    def test_ids_are_unique(self):
        assert Team(name="A").id != Team(name="B").id


class TestVotingCardSet:
    def test_make_default(self):
        cs = VotingCardSet.make_default()
        assert cs.id == "cardset-default"
        assert cs.cards == ["1", "2", "3", "5", "8", "13", "?", "☕️", "♾️"]
        assert cs.name == "Fibonacci Extended"

    def test_custom_card_set(self):
        cs = VotingCardSet(name="T-shirt", cards=["XS", "S", "M", "L", "XL"])
        assert cs.cards[0] == "XS"


class TestAdminConfig:
    def test_singleton_id(self):
        cfg = AdminConfig()
        assert cfg.id == "config"

    def test_defaults(self):
        cfg = AdminConfig()
        assert cfg.base_issue_url is None
        assert cfg.theme_default == ThemePreference.light

    def test_custom_url(self):
        cfg = AdminConfig(base_issue_url="https://jira.example.com/browse/")
        assert cfg.base_issue_url == "https://jira.example.com/browse/"


class TestSession:
    def test_default_status_is_active(self):
        s = Session(team_id="t1", name="Sprint 1", sprint_number="1", card_set_id="cs1")
        assert s.status == SessionStatus.active

    def test_nullable_fields_default_to_none(self):
        s = Session(team_id="t1", name="Sprint 1", sprint_number="1", card_set_id="cs1")
        assert s.leader_participant_id is None
        assert s.completed_at is None


class TestParticipant:
    def test_default_states(self):
        p = Participant(session_id="s1", display_name="Zara", initials="ZR")
        assert p.is_leader is False
        assert p.join_state == JoinState.joined
        assert p.evaluation_state == EvaluationState.active_issue_participating
        assert p.left_at is None

    def test_leader_flag(self):
        p = Participant(session_id="s1", display_name="Sam", initials="SA", is_leader=True)
        assert p.is_leader is True


class TestIssue:
    def test_required_fields(self):
        issue = Issue(
            session_id="s1",
            order_index=0,
            issue_type=IssueType.story,
            issue_key="AUTH-001",
            summary="Login page",
        )
        assert issue.is_active is False
        assert issue.final_estimate is None
        assert issue.revealed_at is None

    def test_issue_type_enum(self):
        bug = Issue(
            session_id="s1",
            order_index=0,
            issue_type=IssueType.bug,
            issue_key="AUTH-002",
            summary="500 error on login",
        )
        assert bug.issue_type == IssueType.bug
        assert bug.issue_type.value == "Bug"


class TestVote:
    def test_default_visibility(self):
        v = Vote(
            session_id="s1",
            issue_id="i1",
            participant_id="p1",
            selected_card="5",
        )
        assert v.visibility_state == VisibilityState.hidden

    def test_timestamps_are_utc(self):
        v = Vote(session_id="s1", issue_id="i1", participant_id="p1", selected_card="3")
        assert v.cast_at.tzinfo == timezone.utc
