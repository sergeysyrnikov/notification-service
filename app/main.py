from fastapi import FastAPI

from app.events.api.router import http_router as events_http_router
from app.events.api.router import ws_router as events_ws_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="notification-service",
        description="Mini notification service (FastAPI)",
        summary="Mini notification service (FastAPI)",
    )
    app.include_router(events_http_router)
    app.include_router(events_ws_router)
    return app


app = create_app()
