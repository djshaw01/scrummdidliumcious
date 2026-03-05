"""Runtime configuration classes for development, testing, and postgres modes."""

import os


class BaseConfig:
    """Shared application defaults across all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    DATA_BACKEND = os.getenv("DATA_BACKEND", "inmemory")


class DevelopmentConfig(BaseConfig):
    """Configuration used for local development."""

    DEBUG = True


class TestingConfig(BaseConfig):
    """Configuration used for test execution."""

    TESTING = True
    DEBUG = False


class PostgresConfig(DevelopmentConfig):
    """Configuration for local postgres-backed runtime."""

    DATA_BACKEND = "postgres"
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://poker_user:dev_password@localhost:5432/scrum_poker",
    )


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "postgres": PostgresConfig,
}


def get_config(config_name: str | None = None) -> type[BaseConfig]:
    """Resolve a configuration class from explicit name or APP_ENV.

    Args:
        config_name: Optional explicit environment name.

    Returns:
        Configuration class object.
    """
    name = config_name or os.getenv("APP_ENV", "development")
    return CONFIG_MAP.get(name, DevelopmentConfig)
