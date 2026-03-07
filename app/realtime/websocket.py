"""Flask-Sock WebSocket endpoint for SCRUM Poker session realtime events."""

from __future__ import annotations

from simple_websocket import Server as WSConnection

from app import sock
from app.services.realtime_event_service import RealtimeEventService


@sock.route("/ws/poker/session/<session_id>")
def poker_session_ws(ws: WSConnection, session_id: str) -> None:
    """WebSocket endpoint for a SCRUM Poker session event stream.

    Clients connect to receive broadcast session events (vote updates,
    reveals, leadership changes) in real time.  Command actions (vote,
    reveal, etc.) are performed via REST endpoints; this channel is
    receive-only for the server except for heartbeat acknowledgement.

    :param ws: Active WebSocket connection managed by Flask-Sock.
    :param session_id: String UUID of the session to subscribe to.
    """
    service = RealtimeEventService.get_instance()
    service.register(session_id, ws)
    try:
        while True:
            # Block waiting for client frames (heartbeat pings).
            # Non-None return means client sent a message; None means timeout.
            data = ws.receive(timeout=60)
            if data is None:
                # Idle timeout — close cleanly.
                break
    except Exception:  # noqa: BLE001
        pass
    finally:
        service.deregister(session_id, ws)
