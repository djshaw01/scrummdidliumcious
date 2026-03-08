"""Unit tests for ThemeService — theme preference storage and retrieval.

Requirement trace:
- Theme preference can be read from Configuration table.
- Theme preference can be written to Configuration table.
- Default theme is 'light' when not configured.
- Invalid theme values default to 'light'.
- Theme changes persist across service instantiations.
"""

from __future__ import annotations

import pytest

from app.models.configuration import Configuration
from app.services.theme_service import ThemeService

# ── Fixtures and helpers ───────────────────────────────────────────────────────


def _ensure_config(db_session) -> Configuration:
    """Ensure configuration singleton exists in database.

    :param db_session: SQLAlchemy session to use.
    :returns: Configuration instance.
    """
    config = db_session.query(Configuration).first()
    if not config:
        config = Configuration(id=1, default_theme="light")
        db_session.add(config)
        db_session.flush()
    return config


# ── ThemeService.get_theme ────────────────────────────────────────────────────


class TestGetTheme:
    """Tests for reading theme preference."""

    def test_get_theme_returns_light_by_default(self, db_session):
        """When no theme is configured, default to 'light'."""
        _ensure_config(db_session)
        config = db_session.query(Configuration).first()
        config.default_theme = None
        db_session.commit()

        svc = ThemeService(db_session)
        theme = svc.get_theme()

        assert theme == "light"

    def test_get_theme_returns_configured_value(self, db_session):
        """When theme is set in Configuration, return that value."""
        config = _ensure_config(db_session)
        config.default_theme = "dark"
        db_session.commit()

        svc = ThemeService(db_session)
        theme = svc.get_theme()

        assert theme == "dark"

    def test_get_theme_returns_light_when_set_to_light(self, db_session):
        """Explicitly configured 'light' theme is returned."""
        config = _ensure_config(db_session)
        config.default_theme = "light"
        db_session.commit()

        svc = ThemeService(db_session)
        theme = svc.get_theme()

        assert theme == "light"

    def test_get_theme_handles_invalid_value_gracefully(self, db_session):
        """Invalid theme values default to 'light'."""
        config = _ensure_config(db_session)
        config.default_theme = "invalid"
        db_session.commit()

        svc = ThemeService(db_session)
        theme = svc.get_theme()

        assert theme == "light"


# ── ThemeService.set_theme ────────────────────────────────────────────────────


class TestSetTheme:
    """Tests for writing theme preference."""

    def test_set_theme_to_dark_persists_value(self, db_session):
        """Setting theme to 'dark' updates Configuration table."""
        _ensure_config(db_session)

        svc = ThemeService(db_session)
        svc.set_theme("dark")

        # Verify in database
        config = db_session.query(Configuration).first()
        assert config.default_theme == "dark"

    def test_set_theme_to_light_persists_value(self, db_session):
        """Setting theme to 'light' updates Configuration table."""
        _ensure_config(db_session)

        svc = ThemeService(db_session)
        svc.set_theme("light")

        # Verify in database
        config = db_session.query(Configuration).first()
        assert config.default_theme == "light"

    def test_set_theme_with_invalid_value_defaults_to_light(self, db_session):
        """Invalid theme value defaults to 'light' when setting."""
        _ensure_config(db_session)

        svc = ThemeService(db_session)
        svc.set_theme("invalid")

        # Should store 'light' instead
        config = db_session.query(Configuration).first()
        assert config.default_theme == "light"

    def test_set_theme_creates_config_if_missing(self, db_session):
        """Setting theme creates Configuration row if it doesn't exist."""
        # Ensure no config exists
        db_session.query(Configuration).delete()
        db_session.commit()

        svc = ThemeService(db_session)
        svc.set_theme("dark")

        # Config should be created
        config = db_session.query(Configuration).first()
        assert config is not None
        assert config.default_theme == "dark"


# ── ThemeService persistence ──────────────────────────────────────────────────


class TestThemePersistence:
    """Tests for theme persistence across service instances."""

    def test_theme_persists_across_service_instantiations(self, db_session):
        """Theme set by one service instance is readable by another."""
        _ensure_config(db_session)

        # Set theme with first service instance
        svc1 = ThemeService(db_session)
        svc1.set_theme("dark")

        # Read with new service instance
        svc2 = ThemeService(db_session)
        theme = svc2.get_theme()

        assert theme == "dark"

    def test_theme_toggle_sequence_persists(self, db_session):
        """Multiple theme changes persist correctly."""
        _ensure_config(db_session)

        svc = ThemeService(db_session)

        # Toggle sequence: light -> dark -> light
        svc.set_theme("light")
        assert svc.get_theme() == "light"

        svc.set_theme("dark")
        assert svc.get_theme() == "dark"

        svc.set_theme("light")
        assert svc.get_theme() == "light"

    def test_theme_survives_session_commit(self, db_session):
        """Theme preference survives transaction commit."""
        _ensure_config(db_session)

        svc = ThemeService(db_session)
        svc.set_theme("dark")
        db_session.commit()

        # Create new service instance after commit
        svc_new = ThemeService(db_session)
        theme = svc_new.get_theme()

        assert theme == "dark"


# ── ThemeService.toggle_theme ─────────────────────────────────────────────────


class TestToggleTheme:
    """Tests for theme toggle convenience method."""

    def test_toggle_theme_switches_from_light_to_dark(self, db_session):
        """Toggling from 'light' switches to 'dark'."""
        _ensure_config(db_session)

        svc = ThemeService(db_session)
        svc.set_theme("light")

        new_theme = svc.toggle_theme()

        assert new_theme == "dark"
        assert svc.get_theme() == "dark"

    def test_toggle_theme_switches_from_dark_to_light(self, db_session):
        """Toggling from 'dark' switches to 'light'."""
        _ensure_config(db_session)

        svc = ThemeService(db_session)
        svc.set_theme("dark")

        new_theme = svc.toggle_theme()

        assert new_theme == "light"
        assert svc.get_theme() == "light"

    def test_toggle_theme_from_default_switches_to_dark(self, db_session):
        """Toggling from default (light) switches to 'dark'."""
        config = _ensure_config(db_session)
        config.default_theme = None
        db_session.commit()

        svc = ThemeService(db_session)
        new_theme = svc.toggle_theme()

        assert new_theme == "dark"
        assert svc.get_theme() == "dark"
