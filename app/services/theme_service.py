"""Theme preference service for light/dark mode management.

This module provides centralized theme preference storage and retrieval
from the Configuration singleton table.
"""

from __future__ import annotations

from typing import Literal

from sqlalchemy.orm import Session as DBSession

from app.models.configuration import Configuration

ThemeMode = Literal["light", "dark"]

# Valid theme values
VALID_THEMES: set[str] = {"light", "dark"}
DEFAULT_THEME: ThemeMode = "light"


class ThemeService:
    """Service for managing theme preferences.

    Handles reading and writing theme mode to the Configuration table,
    with automatic defaults and validation.
    """

    def __init__(self, db_session: DBSession):
        """Initialize ThemeService with a database session.

        :param db_session: SQLAlchemy session for database operations.
        """
        self.db = db_session

    def get_theme(self) -> ThemeMode:
        """Retrieve current theme preference from Configuration.

        :returns: Current theme mode ('light' or 'dark').
                  Defaults to 'light' if not configured or invalid.
        """
        config = self._get_or_create_config()

        theme = config.default_theme
        if theme not in VALID_THEMES:
            return DEFAULT_THEME

        return theme  # type: ignore

    def set_theme(self, theme: str) -> None:
        """Set theme preference in Configuration.

        Invalid values default to 'light'. Changes are committed to database.

        :param theme: Theme mode to set ('light' or 'dark').
        """
        if theme not in VALID_THEMES:
            theme = DEFAULT_THEME

        config = self._get_or_create_config()
        config.default_theme = theme  # type: ignore
        self.db.commit()

    def toggle_theme(self) -> ThemeMode:
        """Toggle between light and dark themes.

        :returns: New theme mode after toggle.
        """
        current = self.get_theme()
        new_theme: ThemeMode = "dark" if current == "light" else "light"
        self.set_theme(new_theme)
        return new_theme

    def _get_or_create_config(self) -> Configuration:
        """Get Configuration singleton or create if missing.

        :returns: Configuration instance.
        """
        config = self.db.query(Configuration).first()
        if not config:
            config = Configuration(id=1, default_theme=DEFAULT_THEME)
            self.db.add(config)
            self.db.flush()
        return config
