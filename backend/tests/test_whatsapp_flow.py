from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.db.chat_threads import get_thread, replace_thread, set_active_plan_id
from app.schemas.chat import DraftPlanFields
from app.services.chat_pipeline import whatsapp_thread_id_for_user
from app.services.whatsapp_logic import get_whatsapp_reply_async


def test_plan_command_replaces_stale_whatsapp_draft() -> None:
    async def _run() -> None:
        user_id = "user-123"
        thread_id = whatsapp_thread_id_for_user(user_id)
        await replace_thread(
            None,
            thread_id,
            messages=[{"role": "user", "content": "milk and oranges"}],
            draft=DraftPlanFields(
                goal="pick up groceries",
                horizon="today",
                available_minutes=20,
                energy="low",
            ),
        )

        reply = await get_whatsapp_reply_async(None, user_id, "plan", "plan do linkedlists assignment")
        doc = await get_thread(None, thread_id)

        assert doc is not None
        assert doc["draft"]["goal"] == "do linkedlists assignment"
        assert doc["messages"] == [{"role": "user", "content": "plan do linkedlists assignment"}]
        assert "BUILD" in reply
        assert "HELP" in reply

    asyncio.run(_run())


def test_unknown_chat_reply_includes_next_commands_when_ready() -> None:
    async def _run() -> None:
        with patch(
            "app.services.whatsapp_logic.run_chat_turn",
            AsyncMock(return_value=SimpleNamespace(reply="Sounds good.", ask_finalize=True)),
        ):
            reply = await get_whatsapp_reply_async(None, "user-123", "unknown", "okay")

        assert "Sounds good." in reply
        assert "BUILD" in reply
        assert "STUCK" in reply
        assert "DONE" in reply
        assert "HELP" in reply

    asyncio.run(_run())


def test_help_command_lists_supported_commands() -> None:
    async def _run() -> None:
        reply = await get_whatsapp_reply_async(None, "user-123", "help", "help")
        assert "PLAN <task>" in reply
        assert "BUILD" in reply
        assert "STUCK" in reply
        assert "DONE" in reply

    asyncio.run(_run())


def test_done_resets_whatsapp_conversation_but_keeps_active_plan() -> None:
    async def _run() -> None:
        user_id = "user-123"
        thread_id = whatsapp_thread_id_for_user(user_id)
        await replace_thread(
            None,
            thread_id,
            messages=[
                {"role": "user", "content": "milk and oranges"},
                {"role": "assistant", "content": "What else do you need from the store?"},
            ],
            draft=DraftPlanFields(
                goal="pick up groceries",
                horizon="today",
                available_minutes=20,
                energy="low",
            ),
        )
        await set_active_plan_id(None, thread_id, "plan-123")

        reply = await get_whatsapp_reply_async(None, user_id, "done", "DONE")

        doc = await get_thread(None, thread_id)
        assert doc is not None
        assert doc["messages"] == []
        assert doc["draft"]["goal"] == ""
        assert doc.get("active_plan_id") == "plan-123"
        assert "PLAN <task>" in reply
        assert "STUCK" in reply
        assert "keep going" not in reply.lower()

    asyncio.run(_run())
