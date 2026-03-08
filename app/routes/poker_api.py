"""SCRUM Poker REST API routes — session detail, voting, reveal, estimate, and completion."""

from __future__ import annotations

import uuid
from typing import Any

from flask import Blueprint, Response, jsonify, request

from app.db import get_db_session
from app.services.realtime_event_service import RealtimeEventService
from app.services.session_service import SessionService, SessionServiceError
from app.services.vote_service import VoteError, VoteService

poker_api_bp = Blueprint("poker_api", __name__, url_prefix="/api/v1")


def _error(message: str, status: int) -> tuple[Response, int]:
    """Return a JSON error response.

    :param message: Error description.
    :param status: HTTP status code.
    :returns: Tuple of JSON response and status code.
    """
    return jsonify({"error": message}), status


# ── Session detail ─────────────────────────────────────────────────────────────


@poker_api_bp.get("/sessions/<session_id>")
def get_session_detail(session_id: str) -> tuple[Response, int]:
    """Return full session detail (issues, participants, active issue).

    :param session_id: String UUID of the session.
    :returns: JSON SessionDetail response.
    """
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        return _error("Invalid session_id.", 400)
    db = get_db_session()
    try:
        detail = SessionService(db).get_session_detail(sid)
        return jsonify(detail), 200
    except SessionServiceError as exc:
        return _error(str(exc), exc.status_code)
    finally:
        db.close()


# ── Issue activation ───────────────────────────────────────────────────────────


@poker_api_bp.post("/sessions/<session_id>/issues/<issue_id>/activate")
def activate_issue(session_id: str, issue_id: str) -> tuple[Response, int]:
    """Activate a navigation issue card (leader action).

    Deactivates the previously active issue and broadcasts an
    ``issue_activated`` event after the transaction commits.

    :param session_id: String UUID of the session.
    :param issue_id: String UUID of the issue to activate.
    :returns: JSON with the activated issue_id and is_active flag.
    """
    try:
        sid = uuid.UUID(session_id)
        iid = uuid.UUID(issue_id)
    except ValueError:
        return _error("Invalid ID format.", 400)
    db = get_db_session()
    try:
        issue = SessionService(db).activate_issue(sid, iid)
        db.commit()
        RealtimeEventService.get_instance().broadcast(
            session_id,
            {"type": "issue_activated", "issue_id": str(issue.id)},
        )
        return jsonify({"issue_id": str(issue.id), "is_active": issue.is_active}), 200
    except SessionServiceError as exc:
        db.rollback()
        return _error(str(exc), exc.status_code)
    finally:
        db.close()


# ── Participant rejoin ─────────────────────────────────────────────────────────


@poker_api_bp.post("/sessions/<session_id>/participants/<participant_id>/rejoin")
def rejoin_active_issue(session_id: str, participant_id: str) -> tuple[Response, int]:
    """Sync a participant back to the current active issue.

    :param session_id: String UUID of the session.
    :param participant_id: String UUID of the participant rejoining.
    :returns: JSON with the active_issue_id (or null if none is active).
    """
    try:
        sid = uuid.UUID(session_id)
        pid = uuid.UUID(participant_id)
    except ValueError:
        return _error("Invalid ID format.", 400)
    db = get_db_session()
    try:
        active = SessionService(db).rejoin_active_issue(sid, pid)
        db.commit()
        return (
            jsonify({"active_issue_id": str(active.id) if active else None}),
            200,
        )
    except SessionServiceError as exc:
        db.rollback()
        return _error(str(exc), exc.status_code)
    finally:
        db.close()


# ── Voting ─────────────────────────────────────────────────────────────────────


@poker_api_bp.put("/sessions/<session_id>/issues/<issue_id>/votes/me")
def upsert_vote(session_id: str, issue_id: str) -> tuple[Response, int]:
    """Cast or change the current participant's vote.

    Request body: ``{"participant_id": "<uuid>", "card_value": "<value>"}``

    Broadcasts a ``vote_cast`` event with the updated vote count after the
    transaction commits.

    :param session_id: String UUID of the session.
    :param issue_id: String UUID of the issue.
    :returns: JSON with the persisted vote id and card_value.
    """
    body: dict[str, Any] = request.get_json(silent=True) or {}
    try:
        sid = uuid.UUID(session_id)
        iid = uuid.UUID(issue_id)
        pid = uuid.UUID(str(body.get("participant_id", "")))
    except (ValueError, AttributeError):
        return _error("Invalid ID format or missing participant_id.", 400)
    card_value = body.get("card_value")
    if not card_value:
        return _error("card_value is required.", 400)
    db = get_db_session()
    try:
        svc = VoteService(db)
        vote = svc.cast_or_change_vote(sid, iid, pid, card_value)
        vote_count = len(list(svc._vote_repo.list_by_issue(iid)))
        db.commit()
        RealtimeEventService.get_instance().broadcast(
            session_id,
            {
                "type": "vote_cast",
                "issue_id": str(iid),
                "vote_count": vote_count,
            },
        )
        return jsonify({"id": str(vote.id), "card_value": vote.card_value}), 200
    except VoteError as exc:
        db.rollback()
        return _error(str(exc), exc.status_code)
    finally:
        db.close()


@poker_api_bp.delete("/sessions/<session_id>/issues/<issue_id>/votes/me")
def delete_vote(session_id: str, issue_id: str) -> tuple[Response, int]:
    """Remove the current participant's vote.

    Participant is identified via the ``?participant_id=<uuid>`` query param.

    Broadcasts a ``vote_removed`` event with the updated vote count after the
    transaction commits.

    :param session_id: String UUID of the session.
    :param issue_id: String UUID of the issue.
    :returns: 204 No Content on success.
    """
    participant_id_str = request.args.get("participant_id", "")
    try:
        sid = uuid.UUID(session_id)
        iid = uuid.UUID(issue_id)
        pid = uuid.UUID(participant_id_str)
    except ValueError:
        return _error("Invalid ID format or missing participant_id.", 400)
    db = get_db_session()
    try:
        svc = VoteService(db)
        svc.remove_vote(sid, iid, pid)
        vote_count = len(list(svc._vote_repo.list_by_issue(iid)))
        db.commit()
        RealtimeEventService.get_instance().broadcast(
            session_id,
            {
                "type": "vote_removed",
                "issue_id": str(iid),
                "vote_count": vote_count,
            },
        )
        return "", 204
    except VoteError as exc:
        db.rollback()
        return _error(str(exc), exc.status_code)
    finally:
        db.close()


# ── Reveal ─────────────────────────────────────────────────────────────────────


@poker_api_bp.post("/sessions/<session_id>/issues/<issue_id>/reveal")
def reveal_votes(session_id: str, issue_id: str) -> tuple[Response, int]:
    """Reveal all votes for an issue (idempotent).

    Broadcasts a ``votes_revealed`` event with the full summary after the
    transaction commits.

    :param session_id: String UUID of the session.
    :param issue_id: String UUID of the issue to reveal.
    :returns: JSON RevealedVoteSummary.
    """
    try:
        sid = uuid.UUID(session_id)
        iid = uuid.UUID(issue_id)
    except ValueError:
        return _error("Invalid ID format.", 400)
    db = get_db_session()
    try:
        summary = VoteService(db).reveal_votes(sid, iid)
        db.commit()
        RealtimeEventService.get_instance().broadcast(
            session_id,
            {"type": "votes_revealed", "issue_id": str(iid), **summary},
        )
        return jsonify(summary), 200
    except VoteError as exc:
        db.rollback()
        return _error(str(exc), exc.status_code)
    finally:
        db.close()


# ── Estimate ───────────────────────────────────────────────────────────────────


@poker_api_bp.post("/sessions/<session_id>/issues/<issue_id>/estimate")
def save_estimate(session_id: str, issue_id: str) -> tuple[Response, int]:
    """Save a selected-card or custom estimate for an issue (leader only).

    Request body: ``{"selected_card_values": [...], "custom_estimate": "..."}``

    Broadcasts an ``estimate_saved`` event after the transaction commits.

    :param session_id: String UUID of the session.
    :param issue_id: String UUID of the issue.
    :returns: JSON with issue_id and final_estimate.
    """
    body: dict[str, Any] = request.get_json(silent=True) or {}
    try:
        sid = uuid.UUID(session_id)
        iid = uuid.UUID(issue_id)
    except ValueError:
        return _error("Invalid ID format.", 400)
    selected: list[str] | None = body.get("selected_card_values")
    custom: str | None = body.get("custom_estimate")
    db = get_db_session()
    try:
        issue = VoteService(db).save_estimate(
            sid,
            iid,
            selected_card_values=selected,
            custom_estimate=custom,
        )
        final_estimate = issue.final_estimate
        db.commit()
        RealtimeEventService.get_instance().broadcast(
            session_id,
            {
                "type": "estimate_saved",
                "issue_id": str(iid),
                "final_estimate": final_estimate,
            },
        )
        return (
            jsonify({"issue_id": str(iid), "final_estimate": final_estimate}),
            200,
        )
    except VoteError as exc:
        db.rollback()
        return _error(str(exc), exc.status_code)
    finally:
        db.close()


# ── Complete session ───────────────────────────────────────────────────────────


@poker_api_bp.post("/sessions/<session_id>/complete")
def complete_session(session_id: str) -> tuple[Response, int]:
    """Mark a session as completed, locking further voting (idempotent).

    Broadcasts a ``session_completed`` event after the transaction commits.

    :param session_id: String UUID of the session to complete.
    :returns: JSON with session_id and final status.
    """
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        return _error("Invalid session_id.", 400)
    db = get_db_session()
    try:
        session = VoteService(db).complete_session(sid)
        db.commit()
        RealtimeEventService.get_instance().broadcast(
            session_id,
            {
                "type": "session_completed",
                "session_id": str(session.id),
            },
        )
        return (
            jsonify({"session_id": str(session.id), "status": session.status}),
            200,
        )
    except VoteError as exc:
        db.rollback()
        return _error(str(exc), exc.status_code)
    finally:
        db.close()
