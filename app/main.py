from fastapi import FastAPI

from app.events.api.router import router as events_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="notification-service",
        description="Mini notification service (FastAPI)",
        summary="Mini notification service (FastAPI)",
    )
    app.include_router(events_router)
    return app


app = create_app()
