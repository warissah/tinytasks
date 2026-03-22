from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_post_session_start_and_end_ok_without_mongo() -> None:
    t0 = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    start = client.post(
        "/session/start",
        json={"task_id": "plan-test-1", "started_at": t0},
    )
    assert start.status_code == 200
    assert start.json()["status"] == "ok"
    end = client.post(
        "/session/end",
        json={
            "task_id": "plan-test-1",
            "ended_at": t0,
            "reflection": "done",
        },
    )
    assert end.status_code == 200
    assert end.json()["reflection"] == "done"
