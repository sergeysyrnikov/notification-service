import asyncio

from app.events.schemas import JobState


class InMemoryJobStateRepository:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._state_by_job_id: dict[str, JobState] = {}

    async def get(self, job_id: str) -> JobState | None:
        async with self._lock:
            return self._state_by_job_id.get(job_id)

    async def upsert(self, state: JobState) -> None:
        async with self._lock:
            self._state_by_job_id[state.job_id] = state
