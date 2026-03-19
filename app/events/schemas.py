from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

EventType = Literal["job.started", "job.progress", "job.finished"]


class EventPayloadStarted(BaseModel):
    status: str


class EventPayloadProgress(BaseModel):
    progress: int = Field(ge=0, le=100)
    status: str


class EventPayloadFinished(BaseModel):
    status: str
    download_url: str | None = None


class EventIn(BaseModel):
    type: EventType
    product: str
    job_id: str
    timestamp: datetime
    payload: dict[str, Any]

    model_config = ConfigDict(extra="forbid")


class WsClientMessage(BaseModel):
    action: Literal["subscribe"]
    job_id: str

    model_config = ConfigDict(extra="forbid")


class JobState(BaseModel):
    job_id: str
    product: str
    status: str
    progress: int | None
    updated_at: datetime
    download_url: str | None = None

    model_config = ConfigDict(from_attributes=True)
