"""Orchestration for chat → draft → finalize (reuses generate_plan only on finalize)."""

from __future__ import annotations

import logging

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.chat_threads import (
    append_message_pair,
    create_thread,
    draft_from_doc,
    ensure_thread,
    get_thread,
    merge_draft,
    save_thread,
    transcript_for_prompt,
)
from app.db.plans import insert_plan
from app.schemas.chat import ChatMessageResponse, DraftPlanFields
from app.schemas.plan import PlanRequest, PlanResponse
from app.services.gemini_chat import apply_llm_draft, generate_chat_turn
from app.services.gemini_plan import generate_plan as gemini_generate_plan
from app.services.mock_plan import build_stub_plan

logger = logging.getLogger(__name__)


async def run_chat_turn(
    db: AsyncIOMotorDatabase | None,
    *,
    thread_id: str | None,
    text: str,
    stable_thread_id: str | None = None,
) -> ChatMessageResponse:
    """
    One user message → assistant reply + updated draft.

    If stable_thread_id is set (e.g. WhatsApp), use that id instead of creating a random one.
    If thread_id is None and stable_thread_id is None, creates a new web thread.
    """
    if stable_thread_id is not None:
        tid = stable_thread_id
        doc = await ensure_thread(db, tid)
    elif thread_id is None:
        tid = await create_thread(db)
        doc = await get_thread(db, tid)
        assert doc is not None
    else:
        tid = thread_id
        doc = await get_thread(db, tid)
        if doc is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown thread_id")

    draft = draft_from_doc(doc)
    transcript = transcript_for_prompt(doc)
    llm_out = generate_chat_turn(transcript=transcript, draft=draft, latest_user=text)
    new_draft = apply_llm_draft(draft, llm_out)
    append_message_pair(doc, text, llm_out.reply)
    merge_draft(doc, new_draft)
    await save_thread(db, doc)

    return ChatMessageResponse(
        thread_id=tid,
        reply=llm_out.reply,
        draft=new_draft,
        ask_finalize=llm_out.ask_finalize,
    )


def _plan_from_draft(d: DraftPlanFields) -> PlanRequest:
    goal = (d.goal or "").strip()
    # Stricter than PlanRequest min_length=1 so vague one-word chats cannot finalize.
    if len(goal) < 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need a clearer goal first — keep chatting, then finalize.",
        )
    return PlanRequest(
        goal=goal,
        horizon=d.horizon,
        available_minutes=d.available_minutes,
        energy=d.energy,
    )


async def run_finalize(
    db: AsyncIOMotorDatabase | None,
    thread_id: str,
) -> PlanResponse:
    doc = await get_thread(db, thread_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown thread_id")

    draft = draft_from_doc(doc)
    request = _plan_from_draft(draft)

    try:
        plan = gemini_generate_plan(request)
    except Exception:
        logger.exception("finalize: Gemini plan failed; using stub")
        plan = build_stub_plan(request.goal)

    if db is not None:
        try:
            await insert_plan(db, request.goal, plan)
        except Exception:
            logger.exception("finalize: failed to persist plan")

    return plan


def whatsapp_thread_id_for_user(user_id: str) -> str:
    return f"wa-{user_id}"
