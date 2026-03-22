from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_twilio_webhook_prefers_user_id_from_stored_phone() -> None:
    mock_db = object()
    app.state.mongo_db = mock_db
    try:
        with patch(
            "app.routers.webhooks_twilio.get_user_id_for_phone",
            AsyncMock(return_value="user-123"),
        ):
            with patch(
                "app.routers.webhooks_twilio.get_whatsapp_reply_async",
                AsyncMock(return_value="reply body"),
            ) as get_reply:
                res = client.post(
                    "/webhooks/twilio",
                    data={"From": "whatsapp:+15551234567", "Body": "stuck"},
                )
    finally:
        app.state.mongo_db = None

    assert res.status_code == 200
    assert "reply body" in res.text
    get_reply.assert_awaited_once_with(mock_db, "user-123", "stuck", "stuck")
