from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_create_guest_user_uses_mongo_when_available() -> None:
    mock_db = object()
    app.state.mongo_db = mock_db
    doc = {
        "user_id": "user-123",
        "email": "user@example.com",
        "phone": "+15551234567",
    }
    try:
        with patch(
            "app.routers.users.create_or_reuse_guest_user",
            AsyncMock(return_value=(doc, True)),
        ) as create_user:
            with patch(
                "app.routers.users.upsert_whatsapp_for_user_id",
                AsyncMock(),
            ) as upsert_wa:
                res = client.post(
                    "/users/guest",
                    json={"email": "USER@example.com", "phone": "(555) 123-4567"},
                )
    finally:
        app.state.mongo_db = None

    assert res.status_code == 200
    assert res.json() == {
        "user_id": "user-123",
        "email": "user@example.com",
        "phone": "+15551234567",
        "is_new_user": True,
        "persistence": "mongo",
    }
    create_user.assert_awaited()
    upsert_wa.assert_awaited_once_with(mock_db, "user-123", "+15551234567")


@pytest.mark.integration
def test_create_guest_user_conflict_returns_409() -> None:
    app.state.mongo_db = object()
    try:
        with patch(
            "app.routers.users.create_or_reuse_guest_user",
            AsyncMock(side_effect=RuntimeError("contact_conflict")),
        ):
            res = client.post(
                "/users/guest",
                json={"email": "user@example.com", "phone": "+15551234567"},
            )
    finally:
        app.state.mongo_db = None

    assert res.status_code == 409
    assert "different existing users" in res.json()["detail"]


@pytest.mark.integration
def test_create_guest_user_demo_fallback_uses_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEMO_USER_ID", "demo-user-001")
    monkeypatch.setenv("DEMO_USER_EMAIL", "demo@example.com")
    monkeypatch.setenv("DEMO_USER_PHONE", "+15550001111")
    from app.config import get_settings

    get_settings.cache_clear()
    res = client.post(
        "/users/guest",
        json={"email": "USER@example.com", "phone": "(555) 123-4567"},
    )
    get_settings.cache_clear()

    assert res.status_code == 200
    assert res.json() == {
        "user_id": "demo-user-001",
        "email": "user@example.com",
        "phone": "+5551234567",
        "is_new_user": False,
        "persistence": "demo_fallback",
    }


@pytest.mark.integration
def test_create_guest_user_demo_fallback_requires_demo_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEMO_USER_ID", raising=False)
    from app.config import get_settings

    get_settings.cache_clear()
    res = client.post(
        "/users/guest",
        json={"email": "user@example.com", "phone": "+15551234567"},
    )
    get_settings.cache_clear()

    assert res.status_code == 503
    assert "MongoDB unavailable" in res.json()["detail"]
