"""Infrastructure layer — repository adapters, CSV import utilities, and wiring helpers."""

from __future__ import annotations

from flask import Flask, current_app

from app.domain.repositories import RepositoryContext


def get_repos() -> RepositoryContext:
    """Return the active :class:`~app.domain.repositories.RepositoryContext`.

    Must be called within a Flask application context (i.e. during request
    handling or inside ``with app.app_context()``).

    Returns:
        The :class:`RepositoryContext` registered on the current Flask app.
    """
    return current_app.extensions["repos"]  # type: ignore[return-value]


def init_repositories(app: Flask) -> None:
    """Create and attach repository instances to the Flask application.

    The backend is chosen from ``app.config["DATA_BACKEND"]``:

    - ``"inmemory"`` (default): fresh in-memory stores populated with seed fixtures.
    - ``"postgres"``: SQLAlchemy adapters (methods not yet implemented; for
      structural validation only until Phase 6+).

    Args:
        app: The Flask application instance to configure.
    """
    backend: str = app.config.get("DATA_BACKEND", "inmemory")

    if backend == "postgres":
        from app.infra.repository_sqlalchemy import create_repositories

        repos = create_repositories()
    else:
        from app.infra.repository_inmemory import create_repositories, seed_repositories

        repos = create_repositories()
        seed_repositories(repos)

    app.extensions["repos"] = repos

