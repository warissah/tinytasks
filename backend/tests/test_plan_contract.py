import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_post_plan_returns_expected_shape() -> None:
    payload = {
        "goal": "Ship hackathon demo",
        "horizon": "today",
        "available_minutes": 90,
        "energy": "medium",
    }
    res = client.post("/plan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "plan_id" in data
    assert data["tiny_first_step"]["title"]
    assert isinstance(data["steps"], list)
    assert data["implementation_intention"]["if_condition"]
