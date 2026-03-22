from __future__ import annotations

import logging

from app.schemas.nudge import NudgeRequest
from app.schemas.plan import PlanRequest
from app.services.gemini_nudge import generate_nudge
from app.services.gemini_plan import generate_plan
from app.services.mock_logic import handle_done, handle_unknown
from app.services.mock_plan import build_stub_plan

try:
    from app.config import get_settings
except Exception:  # pragma: no cover
    get_settings = None

logger = logging.getLogger(__name__)

# Until phone→task lives in Mongo, Twilio sandbox uses this task id for /nudge-style replies.
HACKATHON_DEMO_TASK_ID = "hackathon-demo"


def _has_gemini() -> bool:
    if get_settings is None:
        return False
    try:
        settings = get_settings()
        return bool(getattr(settings, "gemini_api_key", None))
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


def _build_plan_from_text(raw_body: str):
    goal = (raw_body or "").strip()
    if goal.lower().startswith("plan"):
        goal = goal[4:].strip(" :.-")

    if not goal:
        goal = "Help me get started on my task."

    request = PlanRequest(
        goal=goal,
        horizon="today",
        available_minutes=30,
        energy="medium",
    )

    if _has_gemini():
        try:
            return generate_plan(request)
        except Exception:
            logger.exception("Gemini plan generation failed in WhatsApp flow")

    return build_stub_plan(request.goal)


def _build_start_reply(raw_body: str) -> str:
    plan = _build_plan_from_text(raw_body)
    tiny_first = _extract_tiny_first_step(plan)
    if tiny_first:
        return f"Start here: {tiny_first}"

    first_step = _extract_first_step_title(plan)
    if first_step:
        return f"Start here: {first_step}"

    return "Start here: do the smallest possible first step."


def _build_stuck_reply(raw_body: str) -> str:
    context = (raw_body or "").strip() or "WhatsApp stuck"
    if _has_gemini():
        try:
            out = generate_nudge(
                NudgeRequest(
                    task_id=HACKATHON_DEMO_TASK_ID,
                    context=context,
                )
            )
            return f"{out.message}\n\n2 min try: {out.two_minute_action}"
        except Exception:
            logger.exception("Gemini nudge failed in WhatsApp flow")

    return "Got you. Try this: write just ONE bullet point. Only 2 minutes."


def get_whatsapp_reply(user_id: str, command: str, raw_body: str = "") -> str:
    try:
        if command == "start":
            return _build_start_reply(raw_body)

        if command == "plan":
            return _build_start_reply(raw_body)

        if command == "stuck":
            return _build_stuck_reply(raw_body)

        if command == "done":
            return handle_done(user_id)

        return handle_unknown()

    except Exception:
        logger.exception("WhatsApp reply generation failed")
        return "Something went wrong on our side. Please try again."