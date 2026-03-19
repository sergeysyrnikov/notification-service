from fastapi import APIRouter, Depends, HTTPException

from app.events.api.deps import get_events_service
from app.events.schemas import EventIn
from app.events.service import EventsService
from app.events.ws.endpoint import ws_router  # noqa: F401

http_router = APIRouter(prefix="/api/v1/events", tags=["events"])


@http_router.post("", status_code=200, summary="Post an event")
async def post_event(
    event: EventIn,
    service: EventsService = Depends(get_events_service),
) -> dict[str, bool]:
    """
    Принимает новое событие и отправляет его на обработку сервису EventsService.
    Возвращает {"ok": True} при успешной обработке.
    """

    try:
        await service.handle_event(event)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"ok": True}
