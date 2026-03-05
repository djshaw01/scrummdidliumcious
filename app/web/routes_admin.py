"""Admin configuration route handlers.

Full implementation arrives in Phase 6 (US4).
"""

from flask import Blueprint, render_template

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
def index() -> str:
    """Admin configuration page (Phase 6 implementation)."""
    return render_template("admin/index.html")
