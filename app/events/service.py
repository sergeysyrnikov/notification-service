from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from app.events.repository import InMemoryJobStateRepository
from app.events.schemas import (
    EventIn,
    EventPayloadFinished,
    EventPayloadProgress,
    EventPayloadStarted,
    JobState,
)
from app.events.ws_manager import ConnectionManager


class EventsService:
    def __init__(
        self,
        repository: InMemoryJobStateRepository,
        ws_manager: ConnectionManager,
    ) -> None:
        self._repository = repository
        self._ws_manager = ws_manager

    async def handle_event(self, event: EventIn) -> JobState:
        state = await self._apply_event(event)
        await self._repository.upsert(state)

        await self._ws_manager.broadcast_json(
            job_id=event.job_id,
            message={
                "job": state.model_dump(mode="json"),
                "event": event.model_dump(mode="json"),
            },
        )
        return state

    async def subscribe(self, websocket: Any, job_id: str) -> None:
        await self._ws_manager.subscribe(websocket, job_id)
        state = await self._repository.get(job_id)
        if state is None:
            return
        await websocket.send_json({"job": state.model_dump(mode="json")})

    async def disconnect(self, websocket: Any) -> None:
        await self._ws_manager.disconnect(websocket)

    async def _apply_event(self, event: EventIn) -> JobState:
        updated_at = event.timestamp

        if event.type == "job.started":
            payload = _validate_payload(EventPayloadStarted, event.payload)
            return JobState(
                job_id=event.job_id,
                product=event.product,
                status=payload.status,
                progress=None,
                updated_at=updated_at,
            )

        existing = await self._repository.get(event.job_id)
        if existing is None:
            existing = JobState(
                job_id=event.job_id,
                product=event.product,
                status="unknown",
                progress=None,
                updated_at=updated_at,
            )

        if event.type == "job.progress":
            payload = _validate_payload(EventPayloadProgress, event.payload)
            return JobState(
                job_id=existing.job_id,
                product=existing.product,
                status=payload.status,
                progress=payload.progress,
                updated_at=updated_at,
                download_url=existing.download_url,
            )

        if event.type == "job.finished":
            payload = _validate_payload(EventPayloadFinished, event.payload)
            progress = existing.progress
            if payload.status == "success":
                progress = 100
            return JobState(
                job_id=existing.job_id,
                product=existing.product,
                status=payload.status,
                progress=progress,
                updated_at=updated_at,
                download_url=payload.download_url,
            )

        raise ValueError(f"Unsupported event type: {event.type}")


def _validate_payload(model: Any, payload: dict[str, Any]) -> Any:
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise ValueError("Invalid payload") from exc
