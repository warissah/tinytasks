import logging

from fastapi import APIRouter, Form, HTTPException, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

from app.services.command_parser import parse_command
from app.services.whatsapp_logic import get_whatsapp_reply_async

router = APIRouter()
logger = logging.getLogger(__name__)


def map_phone_to_user_id(from_number: str) -> str:
    if not from_number:
        raise HTTPException(status_code=400, detail="Missing From number")
    return from_number.replace("whatsapp:", "")


@router.post("/twilio")
async def twilio_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(""),
):
    # TODO (T3): Validate X-Twilio-Signature with TWILIO_AUTH_TOKEN before accepting webhooks (prod / demo hardening).
    logger.info("twilio inbound from=%s body_len=%s", From, len(Body or ""))

    user_id = map_phone_to_user_id(From)
    command = parse_command(Body)
    db = getattr(request.app.state, "mongo_db", None)
    reply = await get_whatsapp_reply_async(db, user_id, command, Body)

    twiml = MessagingResponse()
    twiml.message(reply)

    return Response(content=str(twiml), media_type="application/xml")
