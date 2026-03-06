"""Pytest configuration and fixtures for the SCRUMMDidliumcious test suite."""

import pytest

from app import create_app


@pytest.fixture(scope="session")
def app():
    """Create a Flask application configured for testing.

    :returns: Configured Flask application instance.
    """
    flask_app = create_app(
        {
            "TESTING": True,
            "APP_ENV": "testing",
            "SECRET_KEY": "test-secret-key",
            "LOGO_ASSET_PATH": "images/scrumm_logo.svg",
        }
    )
    return flask_app


@pytest.fixture()
def client(app):
    """Provide a Flask test client for making HTTP requests.

    :param app: Flask application fixture.
    :returns: Flask test client instance.
    """
    return app.test_client()
