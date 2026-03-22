"""Unit tests for WhatsApp STUCK → nudge task_id resolution (no Mongo)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest


def test_resolve_nudge_task_id_prefers_active_plan_on_thread() -> None:
    async def _run() -> None:
        with patch(
            "app.services.whatsapp_logic.get_active_plan_id_for_thread",
            AsyncMock(return_value="plan-from-thread"),
        ):
            with patch(
                "app.services.whatsapp_logic.find_latest_plan_id_for_phone",
                AsyncMock(return_value="plan-from-phone"),
            ):
                from app.services.whatsapp_logic import resolve_nudge_task_id_for_whatsapp

                r = await resolve_nudge_task_id_for_whatsapp(object(), "+15550001111")
                assert r == "plan-from-thread"

    asyncio.run(_run())


def test_resolve_nudge_task_id_falls_back_to_latest_phone_plan() -> None:
    async def _run() -> None:
        with patch(
            "app.services.whatsapp_logic.get_active_plan_id_for_thread",
            AsyncMock(return_value=None),
        ):
            with patch(
                "app.services.whatsapp_logic.find_latest_plan_id_for_phone",
                AsyncMock(return_value="plan-from-phone"),
            ):
                from app.services.whatsapp_logic import resolve_nudge_task_id_for_whatsapp

                r = await resolve_nudge_task_id_for_whatsapp(object(), "+15550002222")
                assert r == "plan-from-phone"

    asyncio.run(_run())


def test_resolve_nudge_task_id_returns_none_when_unlinked() -> None:
    async def _run() -> None:
        with patch(
            "app.services.whatsapp_logic.get_active_plan_id_for_thread",
            AsyncMock(return_value=None),
        ):
            with patch(
                "app.services.whatsapp_logic.find_latest_plan_id_for_phone",
                AsyncMock(return_value=None),
            ):
                from app.services.whatsapp_logic import resolve_nudge_task_id_for_whatsapp

                r = await resolve_nudge_task_id_for_whatsapp(object(), "+15550003333")
                assert r is None

    asyncio.run(_run())


@pytest.mark.integration
def test_stuck_async_returns_guidance_when_no_plan_and_db() -> None:
    async def _run() -> None:
        with patch(
            "app.services.whatsapp_logic.resolve_nudge_task_id_for_whatsapp",
            AsyncMock(return_value=None),
        ):
            from app.services.whatsapp_logic import _build_stuck_reply_async

            msg = await _build_stuck_reply_async(object(), "+1", "stuck on step 2")
            assert "No plan is linked" in msg
            assert "finalize" in msg.lower()

    asyncio.run(_run())
