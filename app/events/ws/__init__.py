"""
WebSocket transport layer for events.

Keeping this in a separate module makes it easier to later replace the
in-memory hub with a broker-backed implementation, while preserving the
same FastAPI process and URL contract.
"""

from app.events.ws.manager import ConnectionManager

__all__ = ["ConnectionManager"]
