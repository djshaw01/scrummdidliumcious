"""Foundational unit tests for SCRUM Poker repository classes.

Tests cover CRUD operations and domain-specific query methods against an
in-memory SQLite database via the db_session fixture.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.models.configuration import Configuration
from app.models.participant import Participant
from app.models.session import Session as PokerSession
from app.models.storage_issue import StorageIssue
from app.models.team import Team
from app.models.vote import Vote
from app.repositories.configuration_repository import ConfigurationRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.team_repository import TeamRepository
from app.repositories.vote_repository import VoteRepository

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_team(db_session, name: str = "Repo Team") -> Team:
    team = Team(name=name)
    db_session.add(team)
    db_session.flush()
    return team


def _make_session(db_session, team: Team, name: str = "Sprint 1") -> PokerSession:
    s = PokerSession(name=name, team_id=team.id, sprint_number=1)
    db_session.add(s)
    db_session.flush()
    return s


def _make_issue(db_session, session: PokerSession, key: str = "PROJ-1") -> StorageIssue:
    issue = StorageIssue(
        session_id=session.id,
        issue_type="Story",
        issue_key=key,
        summary="Test issue",
    )
    db_session.add(issue)
    db_session.flush()
    return issue


def _make_participant(
    db_session, session: PokerSession, uid: str = "user-1"
) -> Participant:
    p = Participant(session_id=session.id, user_identifier=uid)
    db_session.add(p)
    db_session.flush()
    return p


# ── TeamRepository ────────────────────────────────────────────────────────────


class TestTeamRepository:
    """Tests for TeamRepository CRUD and query methods."""

    def test_save_and_get_by_id(self, db_session):
        """A saved team can be retrieved by primary key."""
        repo = TeamRepository(db_session)
        team = Team(name="Alpha")
        repo.save(team)
        fetched = repo.get_by_id(team.id)
        assert fetched is not None
        assert fetched.name == "Alpha"

    def test_get_by_id_missing_returns_none(self, db_session):
        """get_by_id returns None for an unknown UUID."""
        repo = TeamRepository(db_session)
        assert repo.get_by_id(uuid.uuid4()) is None

    def test_get_by_name_case_insensitive(self, db_session):
        """get_by_name matches regardless of case."""
        repo = TeamRepository(db_session)
        team = Team(name="BetaSquad")
        repo.save(team)
        assert repo.get_by_name("betasquad") is not None
        assert repo.get_by_name("BETASQUAD") is not None

    def test_list_all_returns_saved_teams(self, db_session):
        """list_all returns all persisted teams."""
        repo = TeamRepository(db_session)
        repo.save(Team(name="Gamma"))
        repo.save(Team(name="Delta"))
        all_teams = repo.list_all()
        names = [t.name for t in all_teams]
        assert "Gamma" in names
        assert "Delta" in names

    def test_delete_removes_team(self, db_session):
        """delete removes a team from the database."""
        repo = TeamRepository(db_session)
        team = Team(name="Ephemeral")
        repo.save(team)
        tid = team.id
        repo.delete(team)
        assert repo.get_by_id(tid) is None


# ── ConfigurationRepository ───────────────────────────────────────────────────


class TestConfigurationRepository:
    """Tests for ConfigurationRepository singleton access."""

    def test_get_returns_none_before_creation(self, db_session):
        """get() returns None when configuration row has not been seeded."""
        repo = ConfigurationRepository(db_session)
        # Verify no row exists (fresh transaction)
        result = repo.get()
        assert result is None

    def test_get_or_create_seeds_defaults(self, db_session):
        """get_or_create creates a row with null optional fields on first call."""
        repo = ConfigurationRepository(db_session)
        config = repo.get_or_create()
        assert config.id == 1
        assert config.base_url_for_issues is None
        assert config.default_theme is None

    def test_get_or_create_idempotent(self, db_session):
        """get_or_create returns the same row on repeated calls."""
        repo = ConfigurationRepository(db_session)
        first = repo.get_or_create()
        second = repo.get_or_create()
        assert first.id == second.id

    def test_save_persists_changes(self, db_session):
        """save writes updated field values through to the session."""
        repo = ConfigurationRepository(db_session)
        config = repo.get_or_create()
        config.base_url_for_issues = "https://jira.example.com/browse"
        repo.save(config)
        fetched = repo.get()
        assert fetched is not None
        assert fetched.base_url_for_issues == "https://jira.example.com/browse"


# ── SessionRepository ─────────────────────────────────────────────────────────


class TestSessionRepository:
    """Tests for SessionRepository CRUD and query methods."""

    def test_save_and_get_by_id(self, db_session):
        """A saved session can be retrieved by primary key."""
        repo = SessionRepository(db_session)
        team = _make_team(db_session, "SessionTeam")
        session = PokerSession(name="S1", team_id=team.id, sprint_number=5)
        repo.save(session)
        fetched = repo.get_by_id(session.id)
        assert fetched is not None
        assert fetched.name == "S1"
        assert fetched.sprint_number == 5

    def test_get_by_id_unknown_returns_none(self, db_session):
        """get_by_id returns None for an unknown UUID."""
        repo = SessionRepository(db_session)
        assert repo.get_by_id(uuid.uuid4()) is None

    def test_list_active_filters_status(self, db_session):
        """list_active returns only active sessions."""
        team = _make_team(db_session, "ActiveTeam")
        repo = SessionRepository(db_session)
        active = PokerSession(name="Active", team_id=team.id, sprint_number=1)
        repo.save(active)
        done = PokerSession(
            name="Done",
            team_id=team.id,
            sprint_number=2,
            status="completed",
            completed_at=datetime.now(timezone.utc),
        )
        repo.save(done)
        results = repo.list_active()
        statuses = {s.status for s in results}
        assert "completed" not in statuses
        names = [s.name for s in results]
        assert "Active" in names

    def test_list_by_team(self, db_session):
        """list_by_team returns only sessions for the specified team."""
        team_a = _make_team(db_session, "TeamA-Repos")
        team_b = _make_team(db_session, "TeamB-Repos")
        repo = SessionRepository(db_session)
        sa = PokerSession(name="A-session", team_id=team_a.id, sprint_number=1)
        sb = PokerSession(name="B-session", team_id=team_b.id, sprint_number=1)
        repo.save(sa)
        repo.save(sb)
        a_results = repo.list_by_team(team_a.id)
        assert all(s.team_id == team_a.id for s in a_results)
        b_names = [s.name for s in repo.list_by_team(team_b.id)]
        assert "B-session" in b_names

    def test_delete_removes_session(self, db_session):
        """delete removes a session from the database."""
        team = _make_team(db_session, "DeleteTeam")
        repo = SessionRepository(db_session)
        s = PokerSession(name="ToDelete", team_id=team.id, sprint_number=1)
        repo.save(s)
        sid = s.id
        repo.delete(s)
        assert repo.get_by_id(sid) is None


# ── VoteRepository ────────────────────────────────────────────────────────────


class TestVoteRepository:
    """Tests for VoteRepository CRUD and lookup methods."""

    def _setup(self, db_session):
        """Create a team/session/issue/participant hierarchy for vote tests."""
        team = _make_team(db_session, "VoteRepoTeam")
        session = _make_session(db_session, team, "Vote Session")
        issue = _make_issue(db_session, session, "VR-1")
        participant = _make_participant(db_session, session, "voter-1")
        return issue, participant

    def test_save_and_retrieve_by_issue_and_participant(self, db_session):
        """A saved vote can be found by (issue_id, participant_id)."""
        issue, participant = self._setup(db_session)
        repo = VoteRepository(db_session)
        vote = Vote(
            issue_id=issue.id,
            participant_id=participant.id,
            card_value="8",
        )
        repo.save(vote)
        found = repo.get_by_issue_and_participant(issue.id, participant.id)
        assert found is not None
        assert found.card_value == "8"

    def test_get_returns_none_when_no_vote(self, db_session):
        """get_by_issue_and_participant returns None when vote is absent."""
        issue, participant = self._setup(db_session)
        repo = VoteRepository(db_session)
        result = repo.get_by_issue_and_participant(issue.id, participant.id)
        assert result is None

    def test_list_by_issue_returns_all_votes(self, db_session):
        """list_by_issue returns votes from multiple participants."""
        team = _make_team(db_session, "MultiVoteTeam")
        session = _make_session(db_session, team)
        issue = _make_issue(db_session, session, "MV-1")
        p1 = _make_participant(db_session, session, "voter-a")
        p2 = _make_participant(db_session, session, "voter-b")
        repo = VoteRepository(db_session)
        repo.save(Vote(issue_id=issue.id, participant_id=p1.id, card_value="3"))
        repo.save(Vote(issue_id=issue.id, participant_id=p2.id, card_value="5"))
        votes = repo.list_by_issue(issue.id)
        assert len(votes) == 2
        card_values = {v.card_value for v in votes}
        assert card_values == {"3", "5"}

    def test_delete_removes_vote(self, db_session):
        """delete removes a vote from the database."""
        issue, participant = self._setup(db_session)
        repo = VoteRepository(db_session)
        vote = Vote(issue_id=issue.id, participant_id=participant.id, card_value="13")
        repo.save(vote)
        repo.delete(vote)
        assert repo.get_by_issue_and_participant(issue.id, participant.id) is None
