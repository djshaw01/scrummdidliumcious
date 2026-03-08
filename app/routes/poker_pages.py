"""SCRUM Poker page routes — server-rendered views for the session detail page."""

from __future__ import annotations

import uuid

from flask import Blueprint, abort, render_template

from app.db import get_db_session
from app.services.session_service import SessionService, SessionServiceError

poker_pages_bp = Blueprint("poker_pages", __name__)


@poker_pages_bp.get("/poker")
def poker_entry() -> str:
    """Render the poker entry/lobby page with session listing and new session modal.

    :returns: Rendered HTML for the poker entry page.
    """
    return render_template("poker_entry.html")


@poker_pages_bp.get("/poker/session/<session_id>")
def session_detail(session_id: str) -> str:
    """Render the session detail page with voting cards and status row.

    :param session_id: String UUID of the session.
    :returns: Rendered HTML for the poker session page.
    """
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        abort(404)
    db = get_db_session()
    try:
        detail = SessionService(db).get_session_detail(sid)
    except SessionServiceError:
        abort(404)
    finally:
        db.close()

    # Construct poker_session dict for template compatibility.
    poker_session = {
        "id": detail["id"],
        "name": detail["name"],
        "team_id": detail["team_id"],
        "sprint_number": detail["sprint_number"],
        "status": detail["status"],
        "team_name": detail.get("team_name"),
        "created_at": detail["created_at"],
    }

    return render_template(
        "poker_session.html",
        poker_session=poker_session,
        participants=detail["participants"],
        issues=detail["issues"],
        active_issue_id=detail["active_issue"],
    )
