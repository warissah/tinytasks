from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_post_plan_persists_user_id_when_mongo_available() -> None:
    app.state.mongo_db = MagicMock()
    try:
        with patch("app.routers.plan.insert_plan", AsyncMock()) as insert_plan:
            res = client.post(
                "/plan",
                json={
                    "goal": "Ship hackathon demo",
                    "horizon": "today",
                    "available_minutes": 90,
                    "energy": "medium",
                    "user_id": "user-123",
                    "phone": "+15551234567",
                },
            )
    finally:
        app.state.mongo_db = None

    assert res.status_code == 200
    insert_plan.assert_awaited_once()
    _, kwargs = insert_plan.await_args
    assert kwargs["user_id"] == "user-123"
    assert kwargs["user_phone"] == "+15551234567"
