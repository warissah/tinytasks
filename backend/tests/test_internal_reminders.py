from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.services.mock_plan import build_stub_plan

client = TestClient(app)


def _twilio_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACtest_sid_for_pytest")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "test_auth_token")
    monkeypatch.setenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
    get_settings.cache_clear()


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
def test_internal_reminder_skipped_without_mongodb() -> None:
    """Without MONGODB_URI, app has no mongo_db — route skips before Twilio/destination."""
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
    assert body["status"] == "skipped"
    assert "mongodb" in body["detail"].lower()


@pytest.mark.integration
def test_internal_reminder_accepts_agent_context_without_mongo() -> None:
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
    data = res.json()
    assert data["status"] == "skipped"
    assert "mongodb" in data["detail"].lower()


@pytest.mark.integration
def test_internal_reminder_plan_not_found_with_mock_db() -> None:
    app.state.mongo_db = MagicMock()
    try:
        with patch(
            "app.routers.internal_reminders.get_plan_by_plan_id",
            AsyncMock(return_value=None),
        ):
            res = client.post(
                "/internal/reminders/fire",
                json={
                    "user_id": "whatsapp:+15551234567",
                    "task_id": "missing-plan",
                    "reminder_kind": "check_in_15m",
                },
                headers={"X-Internal-Key": "test-internal-key"},
            )
    finally:
        app.state.mongo_db = None

    assert res.status_code == 200
    assert res.json()["status"] == "skipped"
    assert "No plan found" in res.json()["detail"]


@pytest.mark.integration
def test_internal_reminder_snoozed_until_future() -> None:
    plan = build_stub_plan("Ship the demo with a clear enough goal string here")
    future = datetime.now(UTC) + timedelta(hours=2)
    doc = {
        "plan_id": plan.plan_id,
        "goal": "g",
        "plan": plan.model_dump(mode="json"),
        "created_at": datetime.now(UTC),
        "next_reminder_at": future,
    }
    app.state.mongo_db = MagicMock()
    try:
        with patch(
            "app.routers.internal_reminders.get_plan_by_plan_id",
            AsyncMock(return_value=doc),
        ):
            res = client.post(
                "/internal/reminders/fire",
                json={
                    "user_id": "whatsapp:+15551234567",
                    "task_id": plan.plan_id,
                    "reminder_kind": "check_in_15m",
                },
                headers={"X-Internal-Key": "test-internal-key"},
            )
    finally:
        app.state.mongo_db = None

    assert res.status_code == 200
    d = res.json()["detail"]
    assert res.json()["status"] == "skipped"
    assert "snoozed" in d.lower()


@pytest.mark.integration
def test_internal_reminder_push_back_skips_and_updates() -> None:
    plan = build_stub_plan("Ship the demo with a clear enough goal string here")
    doc = {
        "plan_id": plan.plan_id,
        "goal": "g",
        "plan": plan.model_dump(mode="json"),
        "created_at": datetime.now(UTC),
    }
    mock_db = MagicMock()
    app.state.mongo_db = mock_db
    try:
        with patch(
            "app.routers.internal_reminders.get_plan_by_plan_id",
            AsyncMock(return_value=doc),
        ):
            with patch(
                "app.routers.internal_reminders.update_plan_fields",
                AsyncMock(),
            ) as up:
                res = client.post(
                    "/internal/reminders/fire",
                    json={
                        "user_id": "whatsapp:+15551234567",
                        "task_id": plan.plan_id,
                        "reminder_kind": "check_in_15m",
                        "agent_context": {"push_back_start_minutes": 30},
                    },
                    headers={"X-Internal-Key": "test-internal-key"},
                )
    finally:
        app.state.mongo_db = None

    assert res.status_code == 200
    assert res.json()["status"] == "skipped"
    assert "Snoozed" in res.json()["detail"]
    up.assert_awaited()
    call_kw = up.await_args[0][2]
    assert "next_reminder_at" in call_kw


@pytest.mark.integration
def test_internal_reminder_sent_with_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    _twilio_env(monkeypatch)
    plan = build_stub_plan("Ship the demo with a clear enough goal string here")
    doc = {
        "plan_id": plan.plan_id,
        "goal": "g",
        "plan": plan.model_dump(mode="json"),
        "created_at": datetime.now(UTC),
    }
    app.state.mongo_db = MagicMock()
    try:
        with patch(
            "app.routers.internal_reminders.get_plan_by_plan_id",
            AsyncMock(return_value=doc),
        ):
            with patch(
                "app.routers.internal_reminders.update_plan_fields",
                AsyncMock(),
            ):
                with patch(
                    "app.routers.internal_reminders.send_whatsapp_message",
                    return_value="SM123",
                ):
                    res = client.post(
                        "/internal/reminders/fire",
                        json={
                            "user_id": "whatsapp:+15551234567",
                            "task_id": plan.plan_id,
                            "reminder_kind": "check_in_15m",
                        },
                        headers={"X-Internal-Key": "test-internal-key"},
                    )
    finally:
        app.state.mongo_db = None

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "sent"
    assert "SM123" in body["detail"]


@pytest.mark.integration
def test_internal_reminder_replan_calls_replan_existing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _twilio_env(monkeypatch)
    plan = build_stub_plan("Ship the demo with a clear enough goal string here")
    doc = {
        "plan_id": plan.plan_id,
        "goal": "g",
        "plan": plan.model_dump(mode="json"),
        "created_at": datetime.now(UTC),
    }
    app.state.mongo_db = MagicMock()
    replanned = plan.model_copy(update={"summary": "Replanned summary"})
    try:
        with patch(
            "app.routers.internal_reminders.get_plan_by_plan_id",
            AsyncMock(return_value=doc),
        ):
            with patch(
                "app.routers.internal_reminders.update_plan_fields",
                AsyncMock(),
            ):
                with patch(
                    "app.routers.internal_reminders.replan_existing",
                    return_value=replanned,
                ) as rp:
                    with patch(
                        "app.routers.internal_reminders.send_whatsapp_message",
                        return_value="SM999",
                    ):
                        res = client.post(
                            "/internal/reminders/fire",
                            json={
                                "user_id": "whatsapp:+15551234567",
                                "task_id": plan.plan_id,
                                "reminder_kind": "check_in_15m",
                                "agent_context": {"replan_intensity": "lighter"},
                            },
                            headers={"X-Internal-Key": "test-internal-key"},
                        )
    finally:
        app.state.mongo_db = None

    assert res.status_code == 200
    assert res.json()["status"] == "sent"
    rp.assert_called_once()
