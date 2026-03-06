"""Flask application factory for SCRUMMDidliumcious."""

import os
from pathlib import Path

from flask import Flask
from flask_sock import Sock

sock = Sock()


def create_app(config_overrides: dict | None = None) -> Flask:
    """Create and configure the Flask application.

    :param config_overrides: Optional mapping of config keys to override.
    :returns: Configured Flask application instance.
    """
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # Register root-level images/ directory as a static path at /images
    _register_images_blueprint(app)

    _load_config(app)

    if config_overrides:
        app.config.update(config_overrides)

    sock.init_app(app)

    _register_blueprints(app)

    return app


def _register_images_blueprint(app: Flask) -> None:
    """Register a static blueprint to serve root-level images/ at /images.

    :param app: Flask application instance.
    """
    from flask import Blueprint

    # Resolve the images/ directory relative to the project root
    project_root = Path(app.root_path).parent
    images_dir = project_root / "images"

    if images_dir.is_dir():
        images_bp = Blueprint(
            "images",
            __name__,
            static_folder=str(images_dir),
            static_url_path="/images",
        )
        app.register_blueprint(images_bp)


def _load_config(app: Flask) -> None:
    """Load base configuration from environment variables.

    :param app: Flask application instance to configure.
    """
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["APP_ENV"] = os.environ.get("APP_ENV", "development")
    app.config["DATA_BACKEND"] = os.environ.get("DATA_BACKEND", "inmemory")
    app.config["DATABASE_URL"] = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://scrumm:scrumm@localhost:5432/scrummdidliumcious",
    )
    app.config["LOGO_ASSET_PATH"] = os.environ.get(
        "LOGO_ASSET_PATH", "images/scrumm_logo.svg"
    )
    app.config["THEME_DEFAULT"] = os.environ.get("THEME_DEFAULT", "light")
    app.config["SOCK_SERVER_OPTIONS"] = {"ping_interval": 25}


def _register_blueprints(app: Flask) -> None:
    """Register all route blueprints with the application.

    :param app: Flask application instance.
    """
    from app.routes import home_bp

    app.register_blueprint(home_bp)
