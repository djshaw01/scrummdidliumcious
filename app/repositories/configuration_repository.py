"""Repository for Configuration (singleton) entity."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session as SASession

from app.models.configuration import Configuration

_SINGLETON_ID = 1


class ConfigurationRepository:
    """Data access layer for the singleton Configuration record.

    :param db: Active SQLAlchemy database session.
    """

    def __init__(self, db: SASession) -> None:
        """Initialise with an open database session."""
        self._db = db

    def get(self) -> Configuration | None:
        """Fetch the singleton configuration row.

        :returns: Configuration instance or ``None`` if not yet seeded.
        """
        return self._db.get(Configuration, _SINGLETON_ID)

    def get_or_create(self) -> Configuration:
        """Fetch the singleton row, creating it with defaults if absent.

        :returns: Existing or newly created Configuration instance.
        """
        config = self.get()
        if config is None:
            config = Configuration(
                id=_SINGLETON_ID,
                updated_at=datetime.now(timezone.utc),
            )
            self._db.add(config)
            self._db.flush()
        return config

    def save(self, config: Configuration) -> Configuration:
        """Persist an updated configuration record.

        :param config: Configuration instance with updated values.
        :returns: The saved Configuration instance.
        """
        config.updated_at = datetime.now(timezone.utc)
        self._db.add(config)
        self._db.flush()
        return config
