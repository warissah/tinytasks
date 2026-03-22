"""
Fetch → POST /internal/reminders/fire.

Loads the plan by ``task_id`` (same as ``plan_id`` for MVP). Honors ``next_reminder_at`` snooze,
``agent_context.push_back_start_minutes`` (sets snooze and skips send), and
``agent_context.replan_intensity`` (``smaller_steps`` / ``lighter``) via Gemini + persist.
Requires MongoDB for personalized reminders; without ``MONGODB_URI`` the route skips.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.config import get_settings
from app.db.plans import (
    get_plan_by_plan_id,
    plan_response_from_doc,
    update_plan_fields,
)
from app.schemas.internal import AgentCallbackContext, ReminderFireBody, ReminderFireResponse
from app.schemas.plan import PlanResponse
from app.services.gemini_replan import replan_existing
from app.services.twilio_client import send_whatsapp_message

router = APIRouter()
logger = logging.getLogger(__name__)


def _normalize_whatsapp_addr(value: str) -> str:
    v = value.strip()
    if v.startswith("whatsapp:"):
        return v
    if v.startswith("+"):
        return f"whatsapp:{v}"
    return f"whatsapp:{v}"


def _resolve_destination(user_id: str, demo_to: str | None) -> str | None:
    """Prefer a real address in user_id; else optional REMINDER_DEMO_WHATSAPP_TO for hackathon."""
    u = user_id.strip()
    if u.startswith("whatsapp:"):
        return u
    if u.startswith("+") and any(c.isdigit() for c in u):
        return f"whatsapp:{u.replace(' ', '')}"
    if demo_to and demo_to.strip():
        return _normalize_whatsapp_addr(demo_to)
    return None


def _normalize_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _build_reminder_body(
    plan: PlanResponse,
    agent_context: AgentCallbackContext | None,
) -> str:
    lines = [
        plan.summary,
        "",
        f"Next tiny step: {plan.tiny_first_step.title}",
    ]
    if plan.steps:
        lines.append(f"Then: {plan.steps[0].title}")
    lines.append("")
    lines.append("Still making progress? Reply STUCK for a tiny next step or DONE when you wrap.")
    if agent_context is not None:
        eh = agent_context.energy_hint
        if eh == "low":
            lines.append("(No pressure — take it slow.)")
        elif eh == "high":
            lines.append("(Light momentum — one small move is enough.)")
    lines.append("Not a clinical service. Crisis: 988 or local emergency (US).")
    return "\n".join(lines)[:1500]


@router.post("/reminders/fire", response_model=ReminderFireResponse)
async def fire_reminder(
    request: Request,
    body: ReminderFireBody,
    x_internal_key: str | None = Header(default=None, alias="X-Internal-Key"),
) -> ReminderFireResponse:
    """
    Fetch.ai uAgent → POST here with X-Internal-Key.
    Sends WhatsApp when Twilio + destination + Mongo plan exist; otherwise skips with a clear reason.
    """
    settings = get_settings()
    if not settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="INTERNAL_API_KEY is not set on the server",
        )
    if x_internal_key != settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal key"
        )

    db = getattr(request.app.state, "mongo_db", None)
    ctx_tail = ""
    if body.agent_context is not None:
        ctx_tail = f" agent_context={body.agent_context.model_dump(exclude_none=True)}"

    if db is None:
        return ReminderFireResponse(
            status="skipped",
            detail=(
                "MongoDB not configured; set MONGODB_URI to load the plan for this reminder."
                f"{ctx_tail}"
            ),
        )

    plan_doc: dict[str, Any] | None = await get_plan_by_plan_id(db, body.task_id)
    if plan_doc is None:
        return ReminderFireResponse(
            status="skipped",
            detail=f"No plan found for task_id={body.task_id!r} (expected saved plan_id).{ctx_tail}",
        )

    now = datetime.now(UTC)

    raw_next = plan_doc.get("next_reminder_at")
    if raw_next is not None and isinstance(raw_next, datetime):
        until = _normalize_utc(raw_next)
        if now < until:
            return ReminderFireResponse(
                status="skipped",
                detail=(
                    f"Reminder snoozed until {until.isoformat()}.{ctx_tail}"
                ),
            )

    if body.agent_context is not None and body.agent_context.push_back_start_minutes is not None:
        minutes = body.agent_context.push_back_start_minutes
        next_at = now + timedelta(minutes=minutes)
        await update_plan_fields(
            db,
            body.task_id,
            {"next_reminder_at": next_at},
        )
        return ReminderFireResponse(
            status="skipped",
            detail=(
                f"Snoozed: next reminder after {next_at.isoformat()} "
                f"(push_back {minutes}m).{ctx_tail}"
            ),
        )

    current_plan: PlanResponse
    if (
        body.agent_context is not None
        and body.agent_context.replan_intensity in ("smaller_steps", "lighter")
    ):
        base = plan_response_from_doc(plan_doc)
        current_plan = replan_existing(
            base,
            body.agent_context.replan_intensity,
            body.agent_context.energy_hint,
        )
        await update_plan_fields(
            db,
            body.task_id,
            {
                "plan": current_plan.model_dump(mode="json"),
                "replanned_at": now,
            },
        )
    else:
        current_plan = plan_response_from_doc(plan_doc)

    to = _resolve_destination(body.user_id, settings.reminder_demo_whatsapp_to)
    if not to:
        return ReminderFireResponse(
            status="skipped",
            detail=(
                "No WhatsApp destination: use user_id=whatsapp:+E164 (or +E164), "
                "or set REMINDER_DEMO_WHATSAPP_TO for hackathon demos."
                f"{ctx_tail}"
            ),
        )

    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        return ReminderFireResponse(
            status="skipped",
            detail=f"Twilio credentials not configured on server.{ctx_tail}",
        )

    msg = _build_reminder_body(current_plan, body.agent_context)
    try:
        sid = send_whatsapp_message(to, msg)
        logger.info(
            "reminder sent to=%s twilio_sid=%s kind=%s task_id=%s",
            to,
            sid,
            body.reminder_kind,
            body.task_id,
        )
        await update_plan_fields(db, body.task_id, {"next_reminder_at": None})
        return ReminderFireResponse(
            status="sent",
            detail=f"WhatsApp message created. twilio_sid={sid} to={to}{ctx_tail}",
        )
    except Exception as e:
        logger.exception("Twilio send failed for reminder")
        return ReminderFireResponse(status="failed", detail=str(e)[:500])
