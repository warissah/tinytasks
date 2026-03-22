from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from twilio.request_validator import RequestValidator

from app.config import get_settings
from app.db.users import get_user_id_for_phone
from app.services.command_parser import parse_command
from app.services.twilio_service import (
    build_twiml_message,
    get_or_create_user_id_from_phone,
)
from app.services.whatsapp_logic import get_whatsapp_reply_async

router = APIRouter(tags=["twilio"])
logger = logging.getLogger(__name__)


def get_webhook_url(request: Request) -> str:
    # Respect X-Forwarded-Proto set by reverse proxy (nginx, AWS ALB, etc.)
    scheme = request.headers.get("X-Forwarded-Proto", request.url.scheme)
    host = request.headers.get("X-Forwarded-Host", request.headers.get("host", request.url.hostname))
    return f"{scheme}://{host}{request.url.path}"


def validate_twilio_signature(
    auth_token: str | None,
    url: str,
    form_data: dict[str, str],
    signature: str | None,
) -> bool:
    if not auth_token:
        return True

    if not signature:
        return False

    validator = RequestValidator(auth_token)
    return validator.validate(url, form_data, signature)


@router.post("/twilio")
async def twilio_webhook(request: Request):
    form = await request.form()
    form_data = {k: str(v) for k, v in form.items()}

    signature = request.headers.get("X-Twilio-Signature")
    url = get_webhook_url(request)

    settings = get_settings()
    is_valid = validate_twilio_signature(
        auth_token=settings.twilio_auth_token,
        url=url,
        form_data=form_data,
        signature=signature,
    )

    if not is_valid:
        logger.warning("invalid twilio signature")
        raise HTTPException(status_code=403, detail="Invalid signature")

    from_number = form_data.get("From", "")
    body = form_data.get("Body", "")

    logger.info("twilio inbound from=%s body_len=%s", from_number, len(body or ""))

    db = getattr(request.app.state, "mongo_db", None)
    user_id = await get_user_id_for_phone(db, from_number)
    if user_id is None:
        user_id = get_or_create_user_id_from_phone(from_number)
    command = parse_command(body)

    try:
        reply = await get_whatsapp_reply_async(db, user_id, command, body)
    except Exception:
        logger.exception("error processing twilio webhook from=%s", from_number)
        reply = "Sorry, something went wrong. Please try again later."

    twiml = build_twiml_message(reply)
    return Response(content=twiml, media_type="application/xml")
