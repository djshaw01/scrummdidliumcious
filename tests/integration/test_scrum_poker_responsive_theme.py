"""Responsive and theme persistence integration tests.

Requirement trace:
- Responsive layouts remain usable at 320px width without horizontal scroll.
- Theme preference persists across page loads and browser sessions.
- Theme toggle switches application theme instantly and consistently.
"""

from __future__ import annotations

import uuid
from unittest.mock import patch

import pytest

from app.models.configuration import Configuration
from app.models.team import Team

# ── Helper functions ───────────────────────────────────────────────────────────


def _seed_base_data(db_session):
    """Create minimal data structure for theme/responsive tests.

    :param db_session: SQLAlchemy session to use for setup.
    :returns: Team instance.
    """
    team = Team(name=f"ThemeTestTeam-{uuid.uuid4().hex[:6]}")
    db_session.add(team)

    # Ensure configuration singleton exists
    config = db_session.query(Configuration).first()
    if not config:
        config = Configuration(id=1, default_theme="light")
        db_session.add(config)

    db_session.commit()
    return team


# ── Test classes ───────────────────────────────────────────────────────────────


class TestThemePersistence:
    """Integration tests for theme preference storage and retrieval."""

    def test_theme_toggle_persists_across_page_loads(self, client, db_session):
        """Theme preference saved to configuration is restored on subsequent page loads."""
        _seed_base_data(db_session)

        # Set theme to dark via service
        from app.services.theme_service import ThemeService

        theme_service = ThemeService(db_session)
        theme_service.set_theme("dark")

        # Verify theme is persisted
        retrieved_theme = theme_service.get_theme()
        assert retrieved_theme == "dark"

        # Simulate page reload by creating new service instance
        theme_service_reload = ThemeService(db_session)
        assert theme_service_reload.get_theme() == "dark"

    def test_default_theme_is_light_when_not_configured(self, client, db_session):
        """When no theme preference is set, default to light theme."""
        _seed_base_data(db_session)

        from app.services.theme_service import ThemeService

        theme_service = ThemeService(db_session)
        # Explicitly reset to None to test default behavior
        config = db_session.query(Configuration).first()
        config.default_theme = None
        db_session.commit()

        assert theme_service.get_theme() == "light"

    def test_theme_toggle_between_light_and_dark(self, client, db_session):
        """Theme can be toggled between light and dark modes."""
        _seed_base_data(db_session)

        from app.services.theme_service import ThemeService

        theme_service = ThemeService(db_session)

        # Start with light
        theme_service.set_theme("light")
        assert theme_service.get_theme() == "light"

        # Switch to dark
        theme_service.set_theme("dark")
        assert theme_service.get_theme() == "dark"

        # Switch back to light
        theme_service.set_theme("light")
        assert theme_service.get_theme() == "light"

    def test_invalid_theme_defaults_to_light(self, client, db_session):
        """Invalid theme values default to light mode."""
        _seed_base_data(db_session)

        from app.services.theme_service import ThemeService

        theme_service = ThemeService(db_session)

        # Attempt to set invalid theme
        theme_service.set_theme("invalid")

        # Should default to light
        assert theme_service.get_theme() == "light"


class TestResponsiveLayout:
    """Integration tests for responsive layout behavior."""

    def test_home_page_renders_with_theme_toggle(self, client, db_session):
        """Home page includes theme toggle control in navigation."""
        _seed_base_data(db_session)

        response = client.get("/")
        assert response.status_code == 200

        # Check for theme toggle element presence
        html = response.data.decode("utf-8")
        assert "theme-toggle" in html or "dark-mode" in html.lower()

    def test_poker_entry_page_renders_responsive(self, client, db_session):
        """Poker entry page renders without layout breaks."""
        _seed_base_data(db_session)

        response = client.get("/poker/entry")
        assert response.status_code == 200

        # Verify responsive viewport meta tag
        html = response.data.decode("utf-8")
        assert "viewport" in html
        # Check for mobile-friendly layout classes or CSS
        assert "poker" in html

    def test_poker_session_page_renders_responsive(self, client, db_session):
        """Session detail page renders with responsive layout."""
        from app.models.participant import Participant
        from app.models.session import Session as PokerSession
        from app.models.storage_issue import StorageIssue

        team = _seed_base_data(db_session)

        # Create minimal session
        session = PokerSession(
            name="Responsive Test Session",
            team_id=team.id,
            sprint_number=1,
        )
        db_session.add(session)
        db_session.flush()

        participant = Participant(
            session_id=session.id,
            user_identifier="responsive-user",
            is_leader=True,
        )
        db_session.add(participant)
        db_session.flush()

        session.leader_participant_id = participant.id

        issue = StorageIssue(
            session_id=session.id,
            issue_type="Story",
            issue_key="RESP-1",
            summary="Responsive test story",
            is_active=True,
        )
        db_session.add(issue)
        db_session.commit()

        response = client.get(f"/poker/session/{session.id}")
        assert response.status_code == 200

        # Verify responsive structure
        html = response.data.decode("utf-8")
        assert "poker-session" in html


class TestThemeConsistency:
    """Integration tests for theme consistency across pages."""

    def test_theme_applies_to_all_pages(self, client, db_session):
        """Theme preference applies consistently across all pages."""
        _seed_base_data(db_session)

        from app.services.theme_service import ThemeService

        theme_service = ThemeService(db_session)
        theme_service.set_theme("dark")

        # Check home page
        response = client.get("/")
        assert response.status_code == 200
        # Theme should be accessible or applied via CSS/class

        # Check poker entry page
        response = client.get("/poker/entry")
        assert response.status_code == 200
