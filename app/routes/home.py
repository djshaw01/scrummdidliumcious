"""Home route blueprint for the landing page."""

import os
from pathlib import Path

from flask import Blueprint, current_app, render_template

from app.db import get_db_session
from app.models.landing_page_view import LandingPageView
from app.services.theme_service import ThemeService

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    """Render the branded home landing page.

    :returns: Rendered HTML response for the landing page.
    """
    logo_asset_path = current_app.config.get(
        "LOGO_ASSET_PATH", "images/scrumm_logo.svg"
    )

    logo_available = _resolve_logo_availability(logo_asset_path)

    view = LandingPageView(
        logo_asset_path=logo_asset_path if logo_available else "images/scrumm_logo.svg",
        logo_fallback_text="SCRUMMDidliumcious logo",
    )

    # Get current theme preference
    db = get_db_session()
    theme_service = ThemeService(db)
    theme = theme_service.get_theme()

    return render_template(
        "home.html", view=view, logo_available=logo_available, theme=theme
    )


def _resolve_logo_availability(logo_asset_path: str) -> bool:
    """Check whether the logo asset exists on disk relative to the project root.

    :param logo_asset_path: Relative path to the logo asset (e.g. 'images/scrumm_logo.svg').
    :returns: ``True`` if the file exists on disk, ``False`` otherwise.
    """
    project_root = Path(__file__).parent.parent.parent
    logo_path = project_root / logo_asset_path
    return logo_path.is_file()
