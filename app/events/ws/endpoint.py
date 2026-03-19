from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.events.api.deps import get_events_service
from app.events.schemas import WsClientMessage
from app.events.service import EventsService

ws_router = APIRouter(tags=["events"])


@ws_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    service: EventsService = Depends(get_events_service),
) -> None:
    """Handle WebSocket events for clients.

    Clients must send JSON messages compatible with `WsClientMessage`.
    Invalid messages are answered with an error JSON and the connection
    remains open.
    """
    await websocket.accept()

    try:
        while True:
            raw_message = await websocket.receive_text()
            try:
                message = WsClientMessage.model_validate_json(raw_message)
            except ValidationError:
                await websocket.send_json(
                    {
                        "error": {
                            "code": "invalid_message",
                            "message": "Invalid message payload",
                        }
                    }
                )
                continue

            if message.action == "subscribe":
                await service.subscribe(websocket=websocket, job_id=message.job_id)
    except WebSocketDisconnect:
        pass
    finally:
        await service.disconnect(websocket)
