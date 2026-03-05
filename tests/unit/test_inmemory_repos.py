"""Unit tests for in-memory repository CRUD behaviour and seed data."""

from app.domain.entities import (
    Issue,
    IssueType,
    Participant,
    Session,
    SessionStatus,
    Team,
    Vote,
    VisibilityState,
    VotingCardSet,
)


# ---------------------------------------------------------------------------
# Seed data structural checks
# ---------------------------------------------------------------------------


class TestSeedData:
    def test_two_teams_seeded(self, repos):
        teams = repos.teams.list_all()
        assert len(teams) == 2
        names = {t.name for t in teams}
        assert "Platform Team" in names
        assert "Frontend Team" in names

    def test_three_sessions_seeded(self, repos):
        sessions = repos.sessions.list_all()
        assert len(sessions) == 3

    def test_session_001_is_active(self, repos):
        s = repos.sessions.get_by_id("session-001")
        assert s is not None
        assert s.status == SessionStatus.active

    def test_session_002_is_completed(self, repos):
        s = repos.sessions.get_by_id("session-002")
        assert s is not None
        assert s.status == SessionStatus.completed
        assert s.completed_at is not None

    def test_sessions_sorted_most_recent_first(self, repos):
        sessions = repos.sessions.list_all()
        for i in range(len(sessions) - 1):
            assert sessions[i].created_at >= sessions[i + 1].created_at

    def test_default_card_set_present(self, repos):
        cs = repos.card_sets.get_default()
        assert cs.id == "cardset-default"
        assert "8" in cs.cards
        assert "☕️" in cs.cards

    def test_admin_config_has_base_url(self, repos):
        cfg = repos.admin_config.get()
        assert cfg.base_issue_url is not None and cfg.base_issue_url.startswith("https://")

    def test_session_001_active_issue(self, repos):
        active = repos.issues.get_active_by_session("session-001")
        assert active is not None
        assert active.issue_key == "AUTH-101"
        assert active.is_active is True

    def test_two_votes_on_active_issue(self, repos):
        active = repos.issues.get_active_by_session("session-001")
        votes = repos.votes.list_by_issue(active.id)
        assert len(votes) == 2
        cards = {v.selected_card for v in votes}
        assert cards == {"5", "8"}

    def test_all_votes_hidden_before_reveal(self, repos):
        active = repos.issues.get_active_by_session("session-001")
        for vote in repos.votes.list_by_issue(active.id):
            assert vote.visibility_state == VisibilityState.hidden

    def test_session_001_leader_is_alice(self, repos):
        session = repos.sessions.get_by_id("session-001")
        leader = repos.participants.get_by_id(session.leader_participant_id)
        assert leader is not None
        assert leader.display_name == "Alice Martin"
        assert leader.is_leader is True

    def test_issues_ordered_by_index(self, repos):
        issues = repos.issues.list_by_session("session-001")
        indices = [i.order_index for i in issues]
        assert indices == sorted(indices)


# ---------------------------------------------------------------------------
# Team repository CRUD
# ---------------------------------------------------------------------------


class TestTeamRepository:
    def test_create_and_retrieve(self, empty_repos):
        team = Team(id="t-new", name="New Team")
        empty_repos.teams.create(team)
        found = empty_repos.teams.get_by_id("t-new")
        assert found is not None
        assert found.name == "New Team"

    def test_update(self, empty_repos):
        team = Team(id="t-upd", name="Before")
        empty_repos.teams.create(team)
        team.name = "After"
        empty_repos.teams.update(team)
        assert empty_repos.teams.get_by_id("t-upd").name == "After"

    def test_delete(self, empty_repos):
        team = Team(id="t-del", name="ToDelete")
        empty_repos.teams.create(team)
        empty_repos.teams.delete("t-del")
        assert empty_repos.teams.get_by_id("t-del") is None

    def test_delete_missing_is_noop(self, empty_repos):
        empty_repos.teams.delete("does-not-exist")  # should not raise

    def test_list_all_empty(self, empty_repos):
        assert empty_repos.teams.list_all() == []


# ---------------------------------------------------------------------------
# Session repository
# ---------------------------------------------------------------------------


class TestSessionRepository:
    def test_most_recent_by_team(self, repos):
        recent = repos.sessions.get_most_recent_by_team("team-001")
        assert recent is not None
        # session-001 was created 2 hours ago, session-002 14 days ago
        assert recent.id == "session-001"

    def test_list_by_team_returns_correct_sessions(self, repos):
        platform = repos.sessions.list_by_team("team-001")
        assert len(platform) == 2
        assert all(s.team_id == "team-001" for s in platform)

    def test_most_recent_returns_none_for_unknown_team(self, repos):
        assert repos.sessions.get_most_recent_by_team("team-999") is None


# ---------------------------------------------------------------------------
# Issue repository
# ---------------------------------------------------------------------------


class TestIssueRepository:
    def test_no_active_issue_in_completed_session(self, repos):
        active = repos.issues.get_active_by_session("session-002")
        assert active is None

    def test_four_issues_in_session_001(self, repos):
        issues = repos.issues.list_by_session("session-001")
        assert len(issues) == 4


# ---------------------------------------------------------------------------
# Vote repository
# ---------------------------------------------------------------------------


class TestVoteRepository:
    def test_upsert_replaces_existing_vote(self, repos):
        active = repos.issues.get_active_by_session("session-001")
        original = repos.votes.get_by_participant_and_issue("p-001", active.id)
        assert original.selected_card == "5"

        # change vote
        original.selected_card = "13"
        repos.votes.upsert(original)

        updated = repos.votes.get_by_participant_and_issue("p-001", active.id)
        assert updated.selected_card == "13"
        # only one vote per participant-issue pair
        all_votes = repos.votes.list_by_issue(active.id)
        alice_votes = [v for v in all_votes if v.participant_id == "p-001"]
        assert len(alice_votes) == 1

    def test_delete_by_issue_clears_all_votes(self, repos):
        active = repos.issues.get_active_by_session("session-001")
        repos.votes.delete_by_issue(active.id)
        assert repos.votes.list_by_issue(active.id) == []


# ---------------------------------------------------------------------------
# Admin config repository
# ---------------------------------------------------------------------------


class TestAdminConfigRepository:
    def test_save_and_retrieve(self, empty_repos):
        from app.domain.entities import AdminConfig

        cfg = empty_repos.admin_config.get()
        cfg.base_issue_url = "https://linear.app/myteam/issue/"
        empty_repos.admin_config.save(cfg)
        retrieved = empty_repos.admin_config.get()
        assert retrieved.base_issue_url == "https://linear.app/myteam/issue/"


# ---------------------------------------------------------------------------
# VotingCardSet repository
# ---------------------------------------------------------------------------


class TestVotingCardSetRepository:
    def test_default_always_present(self, empty_repos):
        cs = empty_repos.card_sets.get_default()
        assert cs.id == "cardset-default"

    def test_get_by_id(self, empty_repos):
        cs = empty_repos.card_sets.get_by_id("cardset-default")
        assert cs is not None
        assert "?" in cs.cards
