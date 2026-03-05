"""Application configuration classes for development, testing, and production."""

import os


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY: str = os.environ.get(
        "SECRET_KEY", "dev-only-insecure-secret-change-before-deploy"
    )
    DATA_BACKEND: str = os.environ.get("DATA_BACKEND", "inmemory")
    TESTING: bool = False
    DEBUG: bool = False


class DevelopmentConfig(Config):
    """Local development — in-memory data, debug mode on."""

    DEBUG: bool = True


class TestingConfig(Config):
    """Test-suite configuration — CSRF disabled, deterministic secret key."""

    TESTING: bool = True
    DEBUG: bool = True
    WTF_CSRF_ENABLED: bool = False
    SECRET_KEY: str = "test-only-secret-key"


class PostgresConfig(Config):
    """PostgreSQL-backed configuration for adapter validation."""

    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://poker_user:dev_password@localhost:5432/scrum_poker",
    )


config: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "postgres": PostgresConfig,
}
