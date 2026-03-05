"""SocketIO initialization and room helper utilities."""

from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room

socketio = SocketIO(async_mode="threading", cors_allowed_origins="*")


def init_socketio(app: Flask) -> SocketIO:
    """Initialize SocketIO for the Flask app.

    Args:
        app: Flask application instance.

    Returns:
        Configured SocketIO object.
    """
    socketio.init_app(app)
    return socketio


def session_room(session_id: str) -> str:
    """Build a canonical room name for session-scoped events.

    Args:
        session_id: Session identifier.

    Returns:
        Room name string.
    """
    return f"session:{session_id}"


def join_session_room(session_id: str) -> None:
    """Join current socket connection to a session room.

    Args:
        session_id: Session identifier.

    Returns:
        None.
    """
    join_room(session_room(session_id))


def leave_session_room(session_id: str) -> None:
    """Leave current socket connection from a session room.

    Args:
        session_id: Session identifier.

    Returns:
        None.
    """
    leave_room(session_room(session_id))


def emit_session_event(session_id: str, event_name: str, payload: dict) -> None:
    """Emit a session-scoped event to all subscribers.

    Args:
        session_id: Session identifier.
        event_name: Event name.
        payload: Event payload data.

    Returns:
        None.
    """
    socketio.emit(event_name, payload, to=session_room(session_id))
