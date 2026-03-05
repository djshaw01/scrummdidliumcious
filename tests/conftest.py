"""Shared pytest fixtures available to all test modules."""

import pytest

from app import create_app
from app.domain.repositories import RepositoryContext
from app.infra.repository_inmemory import create_repositories, seed_repositories


@pytest.fixture(scope="session")
def app():
    """Create the Flask application in testing mode for the whole test session."""
    application = create_app("testing")
    yield application


@pytest.fixture()
def client(app):
    """Return a Flask test client with an isolated request context."""
    return app.test_client()


@pytest.fixture()
def runner(app):
    """Return a Flask CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture()
def repos() -> RepositoryContext:
    """Return a fresh, seeded RepositoryContext for each test function.

    Uses a separate set of in-memory repos from the app so tests can mutate
    data freely without affecting other tests or the running application.
    """
    ctx = create_repositories()
    seed_repositories(ctx)
    return ctx


@pytest.fixture()
def empty_repos() -> RepositoryContext:
    """Return a fresh, un-seeded RepositoryContext for tests that need a clean slate."""
    return create_repositories()

