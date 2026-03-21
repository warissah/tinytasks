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


@pytest.mark.integration
def test_internal_reminder_accepts_agent_context() -> None:
    res = client.post(
        "/internal/reminders/fire",
        json={
            "user_id": "u1",
            "task_id": "t1",
            "reminder_kind": "check_in_15m",
            "agent_context": {
                "energy_hint": "low",
                "push_back_start_minutes": 120,
                "replan_intensity": "smaller_steps",
            },
        },
        headers={"X-Internal-Key": "test-internal-key"},
    )
    assert res.status_code == 200
    assert "agent_context" in res.json()["detail"]
