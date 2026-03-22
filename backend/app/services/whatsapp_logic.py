from __future__ import annotations

import logging
import re
from datetime import UTC, datetime

from fastapi import HTTPException

from app.config import get_settings
from app.db.chat_threads import (
    get_active_plan_id_for_thread,
    replace_thread,
    reset_thread_conversation,
)
from app.db.plans import find_latest_plan_id_for_phone, find_latest_plan_id_for_user_id
from app.schemas.chat import DraftPlanFields
from app.schemas.nudge import NudgeRequest
from app.schemas.plan import PlanRequest
from app.services.chat_pipeline import (
    load_linked_plan_for_thread,
    load_or_finalize_thread_plan,
    persist_plan_for_thread,
    run_chat_turn,
    whatsapp_thread_id_for_user,
)
from app.services.gemini_nudge import generate_nudge
from app.services.gemini_plan import generate_plan
from app.services.session_logic import record_session_completion
from app.services.mock_logic import handle_done, handle_unknown
from app.services.mock_plan import build_stub_plan
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# Fallback when Mongo is off or no plan is linked (local / sandbox).
HACKATHON_DEMO_TASK_ID = "hackathon-demo"
_CONTINUE_PATTERNS = (
    re.compile(r"^\s*keep going\s*$", re.IGNORECASE),
    re.compile(r"^\s*continue\s*$", re.IGNORECASE),
    re.compile(r"^\s*what(?:'s| is)? next\??\s*$", re.IGNORECASE),
    re.compile(r"^\s*what should i do next\??\s*$", re.IGNORECASE),
    re.compile(r"^\s*next\b[\s!?]*$", re.IGNORECASE),
    re.compile(r"^\s*go on\s*$", re.IGNORECASE),
)


async def resolve_nudge_task_id_for_whatsapp(
    db: AsyncIOMotorDatabase | None, user_id: str
) -> str | None:
    """
    Prefer chat thread's active_plan_id (finalize on WhatsApp), else latest web plan
    for this phone (POST /plan with matching phone field).
    """
    wa_tid = whatsapp_thread_id_for_user(user_id)
    linked = await get_active_plan_id_for_thread(db, wa_tid)
    if linked:
        return linked
    if db is None:
        return None
    by_user = await find_latest_plan_id_for_user_id(db, user_id)
    if by_user:
        return by_user
    return await find_latest_plan_id_for_phone(db, user_id)


def _has_gemini() -> bool:
    try:
        settings = get_settings()
        return bool(settings.gemini_api_key)
    except Exception:
        return False


def _extract_tiny_first_step(plan) -> str | None:
    if plan is None:
        return None

    if hasattr(plan, "tiny_first_step") and plan.tiny_first_step:
        tiny = plan.tiny_first_step
        title = getattr(tiny, "title", None)
        description = getattr(tiny, "description", None)
        if title and description:
            return f"{title} — {description}"
        if title:
            return str(title)

    if hasattr(plan, "model_dump"):
        data = plan.model_dump()
    elif isinstance(plan, dict):
        data = plan
    else:
        data = None

    if isinstance(data, dict):
        tiny = data.get("tiny_first_step") or {}
        title = tiny.get("title")
        description = tiny.get("description")
        if title and description:
            return f"{title} — {description}"
        if title:
            return str(title)

    return None


def _extract_first_step_title(plan) -> str | None:
    if plan is None:
        return None

    if hasattr(plan, "steps"):
        steps = getattr(plan, "steps") or []
        if steps:
            first = steps[0]
            title = getattr(first, "title", None)
            description = getattr(first, "description", None)
            if title and description:
                return f"{title} — {description}"
            if title:
                return str(title)

    if hasattr(plan, "model_dump"):
        data = plan.model_dump()
    elif isinstance(plan, dict):
        data = plan
    else:
        data = None

    if isinstance(data, dict):
        steps = data.get("steps") or []
        if steps:
            first = steps[0]
            if isinstance(first, dict):
                title = first.get("title")
                description = first.get("description")
                if title and description:
                    return f"{title} — {description}"
                if title:
                    return str(title)
            elif isinstance(first, str):
                return first

    return None


def _request_from_text(raw_body: str) -> PlanRequest:
    goal = (raw_body or "").strip()
    if goal.lower().startswith("plan"):
        goal = goal[4:].strip(" :.-")

    if not goal:
        goal = "Help me get started on my task."

    return PlanRequest(
        goal=goal,
        horizon="today",
        available_minutes=30,
        energy="medium",
    )


def _build_plan_from_request(request: PlanRequest):
    if _has_gemini():
        try:
            return generate_plan(request)
        except Exception:
            logger.exception("Gemini plan generation failed in WhatsApp flow")

    return build_stub_plan(request.goal)


def _build_plan_from_text(raw_body: str):
    request = _request_from_text(raw_body)
    return _build_plan_from_request(request)


async def _seed_whatsapp_thread_for_new_goal(
    db: AsyncIOMotorDatabase | None,
    user_id: str,
    raw_body: str,
    request: PlanRequest,
) -> None:
    user_text = (raw_body or "").strip() or request.goal
    await replace_thread(
        db,
        whatsapp_thread_id_for_user(user_id),
        messages=[{"role": "user", "content": user_text}],
        draft=DraftPlanFields(
            goal=request.goal,
            horizon=request.horizon,
            available_minutes=request.available_minutes,
            energy=request.energy,
        ),
    )


def _default_help_text() -> str:
    return "Commands: PLAN <task>, BUILD, STUCK, DONE. Or just chat. Reply HELP anytime."


def _next_step_hint() -> str:
    return "Next: STUCK if blocked, DONE when finished, or PLAN <task> for something new. Reply HELP anytime."


def _build_ready_hint() -> str:
    return "Next: BUILD for the full plan, STUCK if blocked, or HELP for commands."


def _follow_up_hint_for_done() -> str:
    return "Next: PLAN <task> for something new, STUCK if you need help on this plan, or HELP for commands."


def _append_hint(message: str, hint: str) -> str:
    return f"{message}\n\n{hint}"[:1500]


def _plan_ready_reply(plan) -> str:
    first = getattr(plan.tiny_first_step, "title", None) or "Start with the smallest possible first step."
    return (
        f"Plan ready.\n{plan.summary}\n\nFirst step: {first}\n\n"
        f"(Reply STUCK anytime. Not clinical — crisis: 988.)"
    )


def _continue_on_plan_reply(plan) -> str:
    first = _extract_tiny_first_step(plan) or _extract_first_step_title(plan)
    if first:
        return f"You're still on: {plan.summary}\n\nNext step: {first}"
    return f"You're still on: {plan.summary}\n\nNext step: do the smallest possible next move."


def _is_continue_prompt(raw_body: str) -> bool:
    text = (raw_body or "").strip()
    if not text:
        return False
    return any(pattern.match(text) for pattern in _CONTINUE_PATTERNS)


def _build_stuck_reply_with_task_id(task_id: str, raw_body: str) -> str:
    context = (raw_body or "").strip() or "WhatsApp stuck"
    if _has_gemini():
        try:
            out = generate_nudge(NudgeRequest(task_id=task_id, context=context))
            return f"{out.message}\n\n2 min try: {out.two_minute_action}"
        except Exception:
            logger.exception("Gemini nudge failed in WhatsApp flow")

    return "Got you. Try this: write just ONE bullet point. Only 2 minutes."


def _build_stuck_reply(raw_body: str) -> str:
    """Sync fallback (no DB): demo task id."""
    return _build_stuck_reply_with_task_id(HACKATHON_DEMO_TASK_ID, raw_body)


_NO_PLAN_MSG = (
    "No plan is linked to this number yet. "
    "In the app, create a plan and add your phone number, or chat here and reply finalize when ready. "
    "Then try STUCK again."
)


async def _build_stuck_reply_async(
    db: AsyncIOMotorDatabase | None,
    user_id: str,
    raw_body: str,
) -> str:
    task_id = await resolve_nudge_task_id_for_whatsapp(db, user_id)
    if task_id is None and db is not None:
        return _NO_PLAN_MSG
    if task_id is None:
        task_id = HACKATHON_DEMO_TASK_ID
    return _build_stuck_reply_with_task_id(task_id, raw_body)


def get_whatsapp_reply(user_id: str, command: str, raw_body: str = "") -> str:
    try:
        if command == "start":
            return _append_hint(_plan_ready_reply(_build_plan_from_text(raw_body)), _next_step_hint())

        if command == "plan":
            return _append_hint(_plan_ready_reply(_build_plan_from_text(raw_body)), _next_step_hint())

        if command == "stuck":
            return _build_stuck_reply(raw_body)

        if command == "help":
            return _default_help_text()

        if command == "done":
            return _append_hint(handle_done(user_id), _follow_up_hint_for_done())

        return _append_hint(handle_unknown(), _default_help_text())

    except Exception:
        logger.exception("WhatsApp reply generation failed")
        return "Something went wrong on our side. Please try again."


def _http_detail(exc: HTTPException) -> str:
    d = exc.detail
    if isinstance(d, str):
        return d
    return "Can't build your plan yet. Keep chatting."


async def get_whatsapp_reply_async(
    db: AsyncIOMotorDatabase | None,
    user_id: str,
    command: str,
    raw_body: str = "",
) -> str:
    """
    WhatsApp entry: finalize + free-form chat share one thread per phone (wa-<user_id>).
    start / stuck / done stay on the keyword path.
    Events are written to MongoDB so the web app can poll and reflect changes.
    """
    from app.db.demo_events import insert_demo_event

    try:
        if command == "finalize":
            try:
                plan, created_new = await load_or_finalize_thread_plan(
                    db,
                    whatsapp_thread_id_for_user(user_id),
                    user_id=user_id,
                    reuse_linked_plan=True,
                )
            except HTTPException as e:
                return _http_detail(e)
            if db is not None and created_new:
                await insert_demo_event(db, "new_plan", {
                    "plan": plan.model_dump(mode="json"),
                    "goal": plan.summary,
                })
            return _append_hint(
                _plan_ready_reply(plan),
                "Next: STUCK if blocked, DONE when finished, or PLAN <task> for something new.",
            )

        if command == "stuck":
            return await _build_stuck_reply_async(db, user_id, raw_body)

        if command == "unknown":
            if _is_continue_prompt(raw_body):
                linked = await load_linked_plan_for_thread(
                    db,
                    whatsapp_thread_id_for_user(user_id),
                )
                if linked is not None:
                    return _append_hint(
                        _continue_on_plan_reply(linked[1]),
                        _next_step_hint(),
                    )
            out = await run_chat_turn(
                db,
                thread_id=None,
                text=(raw_body or "").strip() or ".",
                stable_thread_id=whatsapp_thread_id_for_user(user_id),
            )
            hint = _build_ready_hint() if out.ask_finalize else _default_help_text()
            return _append_hint(out.reply, hint)

        if command == "help":
            return _default_help_text()

        if command == "done":
            reply = handle_done(user_id)
            task_id = await resolve_nudge_task_id_for_whatsapp(db, user_id)
            if task_id is not None:
                try:
                    await record_session_completion(
                        db,
                        task_id,
                        datetime.now(UTC),
                        "done",
                    )
                except Exception:
                    logger.exception("WhatsApp done: failed to persist session completion")
            if db is not None:
                await insert_demo_event(db, "task_complete", {})
            await reset_thread_conversation(db, whatsapp_thread_id_for_user(user_id))
            return _append_hint(reply, _follow_up_hint_for_done())

        if command in ("start", "plan"):
            request = _request_from_text(raw_body)
            await _seed_whatsapp_thread_for_new_goal(db, user_id, raw_body, request)
            plan = _build_plan_from_request(request)
            persisted = await persist_plan_for_thread(
                db,
                whatsapp_thread_id_for_user(user_id),
                request,
                plan,
                user_id=user_id,
            )
            if persisted:
                await insert_demo_event(
                    db,
                    "new_plan",
                    {
                        "plan": plan.model_dump(mode="json"),
                        "goal": request.goal,
                    },
                )
            return _append_hint(_plan_ready_reply(plan), _next_step_hint())

        if command == "stuck":
            nudge_data = None
            if _has_gemini():
                try:
                    nudge_data = generate_nudge(
                        NudgeRequest(task_id=HACKATHON_DEMO_TASK_ID, context=raw_body or "stuck via WhatsApp")
                    )
                except Exception:
                    logger.exception("Gemini nudge failed in WhatsApp stuck flow")
            if nudge_data:
                reply = f"{nudge_data.message}\n\n2 min try: {nudge_data.two_minute_action}"
                if db is not None:
                    await insert_demo_event(db, "nudge", {
                        "message": nudge_data.message,
                        "two_minute_action": nudge_data.two_minute_action,
                    })
            else:
                reply = "Got you. Try this: write just ONE bullet point. Only 2 minutes."
                if db is not None:
                    await insert_demo_event(db, "nudge", {
                        "message": reply,
                        "two_minute_action": "Write one bullet point. Just one.",
                    })
            return reply

        return get_whatsapp_reply(user_id, command, raw_body)
    except Exception:
        logger.exception("WhatsApp async reply failed")
        return "Something went wrong on our side. Please try again."
