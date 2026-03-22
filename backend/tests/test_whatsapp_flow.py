from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.db.chat_threads import get_thread, replace_thread, set_active_plan_id
from app.schemas.chat import DraftPlanFields
from app.services.chat_pipeline import load_or_finalize_thread_plan, whatsapp_thread_id_for_user
from app.services.mock_plan import build_stub_plan
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
        assert "STUCK" in reply
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
        assert "HELP" in reply

    asyncio.run(_run())


def test_continue_phrase_uses_linked_plan_instead_of_chat_turn() -> None:
    async def _run() -> None:
        db = object()
        plan = build_stub_plan("finish linked lists assignment")
        with patch(
            "app.services.whatsapp_logic.load_linked_plan_for_thread",
            AsyncMock(return_value=({"plan_id": plan.plan_id}, plan)),
        ):
            with patch(
                "app.services.whatsapp_logic.run_chat_turn",
                AsyncMock(),
            ) as run_chat_turn:
                reply = await get_whatsapp_reply_async(db, "user-123", "unknown", "keep going")

        run_chat_turn.assert_not_awaited()
        assert "You're still on:" in reply
        assert plan.summary in reply
        assert "Next step:" in reply
        assert "STUCK" in reply
        assert "DONE" in reply

    asyncio.run(_run())


def test_what_next_phrase_uses_linked_plan_instead_of_chat_turn() -> None:
    async def _run() -> None:
        db = object()
        plan = build_stub_plan("finish linked lists assignment")
        with patch(
            "app.services.whatsapp_logic.load_linked_plan_for_thread",
            AsyncMock(return_value=({"plan_id": plan.plan_id}, plan)),
        ):
            with patch(
                "app.services.whatsapp_logic.run_chat_turn",
                AsyncMock(),
            ) as run_chat_turn:
                reply = await get_whatsapp_reply_async(db, "user-123", "unknown", "what next")

        run_chat_turn.assert_not_awaited()
        assert "You're still on:" in reply
        assert "Next step:" in reply
        assert "STUCK" in reply

    asyncio.run(_run())


def test_help_command_lists_supported_commands() -> None:
    async def _run() -> None:
        reply = await get_whatsapp_reply_async(None, "user-123", "help", "help")
        assert "PLAN <task>" in reply
        assert "BUILD" in reply
        assert "STUCK" in reply
        assert "DONE" in reply

    asyncio.run(_run())


def test_plan_command_persists_generated_plan_and_emits_event() -> None:
    async def _run() -> None:
        db = object()
        plan = build_stub_plan("do linkedlists assignment")
        with patch(
            "app.services.whatsapp_logic.persist_plan_for_thread",
            AsyncMock(),
        ) as persist_plan:
            with patch(
                "app.services.whatsapp_logic._seed_whatsapp_thread_for_new_goal",
                AsyncMock(),
            ):
                with patch(
                    "app.db.demo_events.insert_demo_event",
                    AsyncMock(),
                ) as insert_demo_event:
                    with patch(
                        "app.services.whatsapp_logic._build_plan_from_request",
                        return_value=plan,
                    ):
                        reply = await get_whatsapp_reply_async(
                            db,
                            "user-123",
                            "plan",
                            "plan do linkedlists assignment",
                        )

        persist_plan.assert_awaited_once()
        args, kwargs = persist_plan.await_args
        assert args[0] is db
        assert args[1] == "wa-user-123"
        assert args[2].goal == "do linkedlists assignment"
        assert args[3] == plan
        assert kwargs["user_id"] == "user-123"
        insert_demo_event.assert_awaited_once()
        event_args = insert_demo_event.await_args.args
        assert event_args[0] is db
        assert event_args[1] == "new_plan"
        assert event_args[2]["goal"] == "do linkedlists assignment"
        assert event_args[2]["plan"]["plan_id"] == plan.plan_id
        assert "Plan ready." in reply
        assert "First step:" in reply
        assert "STUCK" in reply

    asyncio.run(_run())


def test_build_reuses_linked_plan_without_new_event() -> None:
    async def _run() -> None:
        db = object()
        plan = build_stub_plan("do linkedlists assignment")
        with patch(
            "app.services.whatsapp_logic.load_or_finalize_thread_plan",
            AsyncMock(return_value=(plan, False)),
        ) as finalize:
            with patch(
                "app.db.demo_events.insert_demo_event",
                AsyncMock(),
            ) as insert_demo_event:
                reply = await get_whatsapp_reply_async(
                    db,
                    "user-123",
                    "finalize",
                    "BUILD",
                )

        finalize.assert_awaited_once_with(
            db,
            "wa-user-123",
            user_id="user-123",
            reuse_linked_plan=True,
        )
        insert_demo_event.assert_not_awaited()
        assert "Plan ready." in reply
        assert "First step:" in reply

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


def test_done_records_real_session_completion_for_linked_plan() -> None:
    async def _run() -> None:
        with patch(
            "app.services.whatsapp_logic.resolve_nudge_task_id_for_whatsapp",
            AsyncMock(return_value="plan-123"),
        ):
            with patch(
                "app.services.whatsapp_logic.record_session_completion",
                AsyncMock(return_value="backfilled"),
            ) as record_session_completion:
                with patch(
                    "app.db.demo_events.insert_demo_event",
                    AsyncMock(),
                ):
                    with patch(
                        "app.services.whatsapp_logic.reset_thread_conversation",
                        AsyncMock(),
                    ):
                        reply = await get_whatsapp_reply_async(object(), "user-123", "done", "DONE")

        record_session_completion.assert_awaited_once()
        args = record_session_completion.await_args.args
        assert args[1] == "plan-123"
        assert args[3] == "done"
        assert "PLAN <task>" in reply

    asyncio.run(_run())
