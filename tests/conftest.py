"""Shared pytest fixtures available to all test modules."""

import pytest

from app import create_app


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
