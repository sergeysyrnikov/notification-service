from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from app.events.api.deps import get_events_service
from app.events.schemas import EventIn, WsClientMessage
from app.events.service import EventsService

http_router = APIRouter(prefix="/api/v1/events", tags=["events"])
ws_router = APIRouter(tags=["events"])


@http_router.post("", status_code=200, summary="Post an event")
async def post_event(
    event: EventIn,
    service: EventsService = Depends(get_events_service),
) -> dict[str, bool]:
    try:
        await service.handle_event(event)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"ok": True}


@ws_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    service: EventsService = Depends(get_events_service),
) -> None:
    await websocket.accept()

    try:
        while True:
            message = WsClientMessage.model_validate_json(
                await websocket.receive_text()
            )
            if message.action == "subscribe":
                await service.subscribe(websocket=websocket, job_id=message.job_id)
    except WebSocketDisconnect:
        await service.disconnect(websocket)
