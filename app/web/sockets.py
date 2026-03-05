"""Flask-SocketIO event handlers and session-room utilities.

Full implementation arrives in Phase 3 (US1) and is extended in Phase 4 (US2).
"""

from flask_socketio import emit, join_room, leave_room

from app import socketio


@socketio.on("connect")
def handle_connect() -> None:
    """Acknowledge a new SocketIO client connection."""
    emit("connected", {"status": "ok"})


@socketio.on("disconnect")
def handle_disconnect() -> None:
    """Handle client disconnection.

    Leader reassignment on leave is implemented in Phase 3 (US1).
    """


@socketio.on("join_session")
def handle_join_session(data: dict) -> None:
    """Add the client to a session room so it receives session-scoped events.

    Args:
        data: Dict containing a ``session_id`` key.
    """
    session_id = data.get("session_id")
    if session_id:
        join_room(session_id)
        emit("joined", {"session_id": session_id})


@socketio.on("leave_session")
def handle_leave_session(data: dict) -> None:
    """Remove the client from a session room.

    Args:
        data: Dict containing a ``session_id`` key.
    """
    session_id = data.get("session_id")
    if session_id:
        leave_room(session_id)
