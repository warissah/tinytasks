import logging

from fastapi import APIRouter, Form, HTTPException, Response
from twilio.twiml.messaging_response import MessagingResponse

from app.services.command_parser import parse_command
from app.services.whatsapp_logic import get_whatsapp_reply

router = APIRouter()
logger = logging.getLogger(__name__)


def map_phone_to_user_id(from_number: str) -> str:
    if not from_number:
        raise HTTPException(status_code=400, detail="Missing From number")
    return from_number.replace("whatsapp:", "")


@router.post("/twilio")
async def twilio_webhook(
    From: str = Form(...),
    Body: str = Form(""),
):
    logger.info("twilio inbound from=%s body_len=%s", From, len(Body or ""))

    user_id = map_phone_to_user_id(From)
    command = parse_command(Body)
    reply = get_whatsapp_reply(user_id=user_id, command=command, raw_body=Body)

    twiml = MessagingResponse()
    twiml.message(reply)

    return Response(content=str(twiml), media_type="application/xml")
