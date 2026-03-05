"""Admin config repository interface definitions."""

from abc import ABC, abstractmethod

from app.domain.entities.admin_config import AdminConfig


class AdminConfigRepository(ABC):
    """Persistence interface for admin configuration."""

    @abstractmethod
    def get_config(self) -> AdminConfig:
        """Return current admin configuration."""

    @abstractmethod
    def save_config(self, config: AdminConfig) -> AdminConfig:
        """Persist admin configuration changes."""
