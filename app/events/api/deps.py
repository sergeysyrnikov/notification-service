from app.events.repository import InMemoryJobStateRepository
from app.events.service import EventsService
from app.events.ws_manager import ConnectionManager

_repository = InMemoryJobStateRepository()
_ws_manager = ConnectionManager()
_service = EventsService(repository=_repository, ws_manager=_ws_manager)


def get_events_service() -> EventsService:
    return _service
