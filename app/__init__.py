"""SCRUM Poker Flask application factory."""

import os

from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config_name: Configuration key — ``"development"``, ``"testing"``, or
            ``"postgres"``. Defaults to the ``APP_ENV`` environment variable,
            falling back to ``"development"``.

    Returns:
        Configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get("APP_ENV", "development")

    app = Flask(__name__)

    from app.config import config as config_map

    app.config.from_object(config_map[config_name])

    socketio.init_app(app, cors_allowed_origins="*")

    from app.web.routes_sessions import sessions_bp
    from app.web.routes_admin import admin_bp
    from app.web import sockets  # noqa: F401 — registers SocketIO event handlers

    app.register_blueprint(sessions_bp)
    app.register_blueprint(admin_bp)

    return app
