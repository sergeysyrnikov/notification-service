import asyncio
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._subscriptions_by_job_id: dict[str, set[WebSocket]] = defaultdict(set)

    async def subscribe(self, websocket: WebSocket, job_id: str) -> None:
        async with self._lock:
            self._subscriptions_by_job_id[job_id].add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            empty_job_ids: list[str] = []
            for job_id, subscribers in self._subscriptions_by_job_id.items():
                subscribers.discard(websocket)
                if not subscribers:
                    empty_job_ids.append(job_id)

            for job_id in empty_job_ids:
                self._subscriptions_by_job_id.pop(job_id, None)

    async def broadcast_json(self, job_id: str, message: dict) -> None:
        async with self._lock:
            subscribers = list(self._subscriptions_by_job_id.get(job_id, set()))

        dead: list[WebSocket] = []
        for websocket in subscribers:
            try:
                await websocket.send_json(message)
            except Exception:
                dead.append(websocket)

        for websocket in dead:
            await self.disconnect(websocket)
