"""
Fetch → POST /internal/reminders/fire.

TODO (deferred from MVP / master plan — not implemented here yet):
- Load user + task/plan from Mongo using body.user_id and body.task_id; merge last WhatsApp thread state.
- Honor agent_context.push_back_start_minutes by persisting next_reminder_at (snooze).
- When agent_context.replan_intensity is smaller_steps or lighter, call Gemini and persist updated plan copy.
- Resolve WhatsApp destination from Mongo (user_id → phone) instead of only E.164 in user_id / REMINDER_DEMO_WHATSAPP_TO.
- Use task_id / plan content in the outbound message when a stored plan exists.
"""

import logging

from fastapi import APIRouter, Header, HTTPException, status

from app.config import get_settings
from app.schemas.internal import ReminderFireBody, ReminderFireResponse
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
    """Prefer a real address in user_id; else optional REMINDER_DEMO_WHATSAPP_TO for hackathon.

    TODO: Look up user_id in Mongo and return stored whatsapp:+E164 (drop demo override once that exists).
    """
    u = user_id.strip()
    if u.startswith("whatsapp:"):
        return u
    if u.startswith("+") and any(c.isdigit() for c in u):
        return f"whatsapp:{u.replace(' ', '')}"
    if demo_to and demo_to.strip():
        return _normalize_whatsapp_addr(demo_to)
    return None


def _build_reminder_body(body: ReminderFireBody) -> str:
    # TODO: Pass agent_context + task state into Gemini for adaptive copy; append tiny_first_step from DB when available.
    lines = [
        "Quick check-in from your ADHD coach (hackathon demo).",
        "Still making progress? Reply STUCK for a tiny next step or DONE when you wrap.",
    ]
    if body.agent_context is not None:
        # TODO: agent_context is echoed for debugging only; wire push_back / replan / energy into Mongo + Gemini above.
        ctx = body.agent_context.model_dump(exclude_none=True)
        if ctx:
            lines.append(f"(Agent hint: {ctx})")
    lines.append("Not a clinical service. Crisis: 988 or local emergency (US).")
    text = "\n".join(lines)
    return text[:1500]


@router.post("/reminders/fire", response_model=ReminderFireResponse)
def fire_reminder(
    body: ReminderFireBody,
    x_internal_key: str | None = Header(default=None, alias="X-Internal-Key"),
) -> ReminderFireResponse:
    """
    Fetch.ai uAgent → POST here with X-Internal-Key.
    Sends a short WhatsApp when Twilio + destination are configured; otherwise skips with a clear reason.
    """
    settings = get_settings()
    if not settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="INTERNAL_API_KEY is not set on the server",
        )
    if x_internal_key != settings.internal_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal key")

    # TODO: After Mongo load, skip send if session completed / user snoozed / no pending reminder for task_id.
    to = _resolve_destination(body.user_id, settings.reminder_demo_whatsapp_to)
    ctx_tail = ""
    if body.agent_context is not None:
        ctx_tail = f" agent_context={body.agent_context.model_dump(exclude_none=True)}"

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

    msg = _build_reminder_body(body)
    try:
        sid = send_whatsapp_message(to, msg)
        logger.info("reminder sent to=%s twilio_sid=%s kind=%s", to, sid, body.reminder_kind)
        return ReminderFireResponse(
            status="sent",
            detail=f"WhatsApp message created. twilio_sid={sid} to={to}{ctx_tail}",
        )
    except Exception as e:
        logger.exception("Twilio send failed for reminder")
        return ReminderFireResponse(status="failed", detail=str(e)[:500])
