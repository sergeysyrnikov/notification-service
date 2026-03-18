from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import create_app


def test_post_events_valid_sequence_returns_200() -> None:
    client = TestClient(create_app())
    ts = (
        datetime(2026, 3, 13, 10, 0, tzinfo=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
    job_id = "http-123"

    response = client.post(
        "/api/v1/events",
        json={
            "type": "job.started",
            "product": "import",
            "job_id": job_id,
            "timestamp": ts,
            "payload": {"status": "started"},
        },
    )
    assert response.status_code == 200

    response = client.post(
        "/api/v1/events",
        json={
            "type": "job.progress",
            "product": "import",
            "job_id": job_id,
            "timestamp": ts,
            "payload": {"progress": 42, "status": "running"},
        },
    )
    assert response.status_code == 200

    response = client.post(
        "/api/v1/events",
        json={
            "type": "job.finished",
            "product": "import",
            "job_id": job_id,
            "timestamp": ts,
            "payload": {
                "status": "success",
                "download_url": "https://example.com/file.csv",
            },
        },
    )
    assert response.status_code == 200


def test_post_events_missing_required_fields_returns_422() -> None:
    client = TestClient(create_app())
    response = client.post("/api/v1/events", json={"job_id": "123"})
    assert response.status_code == 422


def test_post_events_invalid_payload_returns_422() -> None:
    client = TestClient(create_app())
    ts = (
        datetime(2026, 3, 13, 10, 0, tzinfo=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
    job_id = "http-invalid-123"

    response = client.post(
        "/api/v1/events",
        json={
            "type": "job.progress",
            "product": "import",
            "job_id": job_id,
            "timestamp": ts,
            "payload": {"progress": 999, "status": "running"},
        },
    )
    assert response.status_code == 422
