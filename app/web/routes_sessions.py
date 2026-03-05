"""Session, history, and voting route handlers.

Implementation is phased:
- History (GET /)               — Phase 5 (US3)
- New Session (GET /POST)       — Phase 4 (US2)
- Session Detail (GET)          — Phase 3 (US1)
"""

from flask import Blueprint, render_template

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/")
def history() -> str:
    """Entry/history page listing all sessions (Phase 5 implementation)."""
    return render_template("history/index.html")


@sessions_bp.route("/sessions/new")
def new_session() -> str:
    """New session creation page with CSV upload (Phase 4 implementation)."""
    return render_template("session/new.html")


@sessions_bp.route("/sessions/<session_id>")
def session_detail(session_id: str) -> str:
    """Session detail page with live voting (Phase 3 implementation).

    Args:
        session_id: Unique identifier of the session to display.
    """
    return render_template("session/detail.html", session_id=session_id)
