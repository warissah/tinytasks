import logging
from typing import Any

from fastapi import HTTPException

from app.config import get_settings
from app.schemas.nudge import NudgeRequest
from app.services.chat_pipeline import run_chat_turn, run_finalize, whatsapp_thread_id_for_user
from app.services.gemini_nudge import generate_nudge
from app.services.mock_logic import handle_done, handle_stuck, handle_unknown
from app.services.mock_plan import build_stub_plan
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# Until phone→task/plan lives in Mongo, Twilio uses this task id for /nudge-style replies.
# TODO: Resolve task_id (and optional plan_id) from user_id for STUCK/DONE/start flows.
HACKATHON_DEMO_TASK_ID = "hackathon-demo"


def _extract_first_step(plan: Any) -> str | None:
    """
    Safely extract the first step from different possible PlanResponse shapes.
    Works whether build_stub_plan returns:
    - a Pydantic model
    - a dict
    - steps as strings
    - steps as objects/dicts with title/text/description
    """
    if plan is None:
        return None

    # Pydantic model -> dict
    if hasattr(plan, "model_dump"):
        data = plan.model_dump()
    elif isinstance(plan, dict):
        data = plan
    else:
        data = None

    # Case 1: dict-like object with a steps list
    if isinstance(data, dict):
        steps = data.get("steps") or data.get("tasks") or data.get("subtasks") or []
        if steps:
            first = steps[0]
            if isinstance(first, str):
                return first
            if isinstance(first, dict):
                return (
                    first.get("title")
                    or first.get("text")
                    or first.get("description")
                    or first.get("task")
                )

    # Case 2: object with steps/tasks/subtasks attributes
    for attr in ("steps", "tasks", "subtasks"):
        if hasattr(plan, attr):
            steps = getattr(plan, attr) or []
            if steps:
                first = steps[0]
                if isinstance(first, str):
                    return first
                if isinstance(first, dict):
                    return (
                        first.get("title")
                        or first.get("text")
                        or first.get("description")
                        or first.get("task")
                    )
                for field in ("title", "text", "description", "task"):
                    if hasattr(first, field):
                        value = getattr(first, field)
                        if value:
                            return str(value)

    return None


def get_whatsapp_reply(user_id: str, command: str, raw_body: str = "") -> str:
    try:
        if command == "start":
            plan = build_stub_plan("Help me get started on my task.")
            first_step = _extract_first_step(plan)

            if first_step:
                return f"Start here: {first_step}"

            return "Start here: do the smallest possible first step."

        if command == "stuck":
            settings = get_settings()
            if settings.gemini_api_key:
                try:
                    out = generate_nudge(
                        NudgeRequest(
                            task_id=HACKATHON_DEMO_TASK_ID,
                            context=(raw_body or "").strip() or "WhatsApp stuck",
                        )
                    )
                    return f"{out.message}\n\n2 min try: {out.two_minute_action}"
                except Exception:
                    logger.exception("Gemini nudge from WhatsApp stuck failed")
            return handle_stuck(user_id)

        if command == "done":
            return handle_done(user_id)

        return handle_unknown()

    except Exception as e:
        print(f"[WhatsApp Error] {e}")
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
    """
    try:
        if command == "finalize":
            try:
                plan = await run_finalize(db, whatsapp_thread_id_for_user(user_id))
            except HTTPException as e:
                return _http_detail(e)
            first = plan.tiny_first_step.title
            return (
                f"Plan ready.\n{plan.summary}\n\nFirst step: {first}\n\n"
                f"(Reply STUCK anytime. Not clinical — crisis: 988.)"
            )[:1500]

        if command == "unknown":
            out = await run_chat_turn(
                db,
                thread_id=None,
                text=(raw_body or "").strip() or ".",
                stable_thread_id=whatsapp_thread_id_for_user(user_id),
            )
            return out.reply[:1500]

        return get_whatsapp_reply(user_id, command, raw_body)
    except Exception:
        logger.exception("WhatsApp async reply failed")
        return "Something went wrong on our side. Please try again."