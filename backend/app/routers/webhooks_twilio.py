from __future__ import annotations

import logging

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import Response
from twilio.request_validator import RequestValidator

from app.services.twilio_service import (
    build_twiml_message,
    get_or_create_user_id_from_phone,
    normalize_command,
)
from app.services.whatsapp_logic import get_whatsapp_reply

try:
    from app.core.config import settings
except Exception:  # pragma: no cover
    settings = None

try:
    from app.config import get_settings
except Exception:  # pragma: no cover
    get_settings = None

router = APIRouter(tags=["twilio"])
logger = logging.getLogger(__name__)


def _get_setting(name: str, default=None):
    if settings is not None and hasattr(settings, name):
        value = getattr(settings, name)
        return default if value is None else value

    if get_settings is not None:
        cfg = get_settings()
        if hasattr(cfg, name):
            value = getattr(cfg, name)
            return default if value is None else value

    return default


def validate_twilio_signature(request: Request, form_data: dict[str, str]) -> bool:
    auth_token = _get_setting("TWILIO_AUTH_TOKEN", "")
    if not auth_token:
        return True

    validator = RequestValidator(auth_token)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    return validator.validate(url, form_data, signature)


@router.post("/twilio")
async def twilio_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(""),
):
    logger.info("twilio inbound from=%s body_len=%s", From, len(Body or ""))

    user_id = map_phone_to_user_id(From)
    command = parse_command(Body)
    reply = get_whatsapp_reply(user_id=user_id, command=command, raw_body=Body)

    twiml = build_twiml_message(reply)
    return Response(content=twiml, media_type="application/xml")