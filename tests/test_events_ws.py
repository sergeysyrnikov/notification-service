from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import create_app


def test_ws_subscribe_sends_existing_state_immediately() -> None:
    app = create_app()
    client = TestClient(app)

    ts = (
        datetime(2026, 3, 13, 10, 0, tzinfo=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
    job_id = "ws-existing-123"
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

    with client.websocket_connect("/ws") as ws:
        ws.send_json({"action": "subscribe", "job_id": job_id})
        message = ws.receive_json()
        assert message["job"]["job_id"] == job_id
        assert message["job"]["status"] == "started"


def test_ws_receives_broadcast_on_new_event() -> None:
    app = create_app()
    client = TestClient(app)
    ts = (
        datetime(2026, 3, 13, 10, 0, tzinfo=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
    job_id = "ws-broadcast-123"

    with client.websocket_connect("/ws") as ws:
        ws.send_json({"action": "subscribe", "job_id": job_id})

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

        message = ws.receive_json()
        assert message["job"]["job_id"] == job_id
        assert message["job"]["progress"] == 42
        assert message["event"]["type"] == "job.progress"


def test_ws_does_not_receive_events_for_unsubscribed_job_id() -> None:
    app = create_app()
    client = TestClient(app)
    ts = (
        datetime(2026, 3, 13, 10, 0, tzinfo=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )

    subscribed_job_id = "ws-sub-123"
    other_job_id = "ws-other-123"

    with client.websocket_connect("/ws") as ws:
        ws.send_json({"action": "subscribe", "job_id": subscribed_job_id})

        response = client.post(
            "/api/v1/events",
            json={
                "type": "job.progress",
                "product": "import",
                "job_id": other_job_id,
                "timestamp": ts,
                "payload": {"progress": 7, "status": "running"},
            },
        )
        assert response.status_code == 200

        response = client.post(
            "/api/v1/events",
            json={
                "type": "job.progress",
                "product": "import",
                "job_id": subscribed_job_id,
                "timestamp": ts,
                "payload": {"progress": 8, "status": "running"},
            },
        )
        assert response.status_code == 200

        message = ws.receive_json()
        assert message["job"]["job_id"] == subscribed_job_id
        assert message["event"]["type"] == "job.progress"
