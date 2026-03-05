"""Application factory and extension setup for the SCRUM poker app."""

from flask import Flask

from app.config import get_config
from app.web.sockets import init_socketio


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application instance.

    Args:
        config_name: Optional configuration key to override APP_ENV.

    Returns:
        Configured Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(get_config(config_name))
    init_socketio(app)

    # Route blueprints and SocketIO setup are wired in later phases.
    return app
