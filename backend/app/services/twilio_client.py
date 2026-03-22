from __future__ import annotations

from twilio.rest import Client

from app.config import get_settings


def get_twilio_client() -> Client:
    settings = get_settings()
    account_sid = settings.twilio_account_sid
    auth_token = settings.twilio_auth_token
    if not account_sid or not auth_token:
        raise RuntimeError("Missing Twilio credentials")

    return Client(account_sid, auth_token)


def send_whatsapp_message(to_number: str, body: str) -> str:
    settings = get_settings()
    client = get_twilio_client()

    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"

    from_number = settings.twilio_whatsapp_from or "whatsapp:+14155238886"

    message = client.messages.create(
        from_=from_number,
        to=to_number,
        body=body,
    )
    return message.sid
