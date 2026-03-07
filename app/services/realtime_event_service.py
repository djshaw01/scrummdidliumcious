"""Realtime event service — thread-safe in-process pub/sub for session broadcasts."""

from __future__ import annotations

import json
import logging
import threading
from typing import Any

from simple_websocket import Server as WSConnection

logger = logging.getLogger(__name__)


class RealtimeEventService:
    """Thread-safe in-process pub/sub channel for SCRUM Poker session events.

    Maintains a registry of active WebSocket connections keyed by session ID
    and provides a :meth:`broadcast` method called after committed DB writes.

    Usage::

        service = RealtimeEventService.get_instance()
        service.broadcast(session_id, {"type": "vote_cast", "participant_id": "..."})
    """

    _instance: "RealtimeEventService | None" = None
    _class_lock: threading.Lock = threading.Lock()

    def __init__(self) -> None:
        """Initialise with an empty connection registry."""
        self._connections: dict[str, list[WSConnection]] = {}
        self._registry_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "RealtimeEventService":
        """Return the application-scoped singleton instance.

        :returns: Shared RealtimeEventService instance.
        """
        with cls._class_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def register(self, session_id: str, ws: WSConnection) -> None:
        """Register a WebSocket connection for broadcast delivery.

        :param session_id: String UUID of the session to subscribe to.
        :param ws: Active WebSocket connection to register.
        """
        with self._registry_lock:
            self._connections.setdefault(session_id, []).append(ws)

    def deregister(self, session_id: str, ws: WSConnection) -> None:
        """Deregister a WebSocket connection on close or error.

        :param session_id: String UUID of the session.
        :param ws: WebSocket connection to remove.
        """
        with self._registry_lock:
            conns = self._connections.get(session_id, [])
            if ws in conns:
                conns.remove(ws)
            if not conns:
                self._connections.pop(session_id, None)

    def broadcast(self, session_id: str, event: dict[str, Any]) -> None:
        """Broadcast a JSON event to all connected clients of a session.

        Must only be called after the originating database transaction has been
        committed to ensure clients receive consistent state.

        :param session_id: String UUID of the target session.
        :param event: Event payload dict; serialised to JSON before sending.
        """
        payload = json.dumps(event)
        with self._registry_lock:
            targets = list(self._connections.get(session_id, []))
        dead: list[WSConnection] = []
        for ws in targets:
            try:
                ws.send(payload)
            except Exception as exc:  # noqa: BLE001
                logger.debug("Removing stale WebSocket connection: %s", exc)
                dead.append(ws)
        for ws in dead:
            self.deregister(session_id, ws)

    def connection_count(self, session_id: str) -> int:
        """Return the count of active WebSocket connections for a session.

        :param session_id: String UUID of the session.
        :returns: Number of registered connections.
        """
        with self._registry_lock:
            return len(self._connections.get(session_id, []))
