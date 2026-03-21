import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_internal_reminder_requires_key() -> None:
    res = client.post(
        "/internal/reminders/fire",
        json={
            "user_id": "u1",
            "task_id": "t1",
            "reminder_kind": "check_in_15m",
        },
    )
    assert res.status_code == 401


@pytest.mark.integration
def test_internal_reminder_ok_with_key() -> None:
    res = client.post(
        "/internal/reminders/fire",
        json={
            "user_id": "u1",
            "task_id": "t1",
            "reminder_kind": "check_in_15m",
        },
        headers={"X-Internal-Key": "test-internal-key"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "queued_stub"
