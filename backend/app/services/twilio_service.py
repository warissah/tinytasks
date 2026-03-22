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


def build_twiml_message(message: str) -> str:
    escaped = (
        (message or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped}</Message></Response>'


def normalize_command(body: str) -> str:
    text = (body or "").strip().lower()
    if not text:
        return "unknown"
    return text.split()[0]


def get_or_create_user_id_from_phone(phone_number: str) -> str:
    # For hackathon demo, user_id is the normalized phone number.
    return (phone_number or "").replace("whatsapp:", "").strip()


def normalize_whatsapp_to(phone: str) -> str:
    phone = (phone or "").strip()
    if not phone:
        raise ValueError("Missing destination phone number")
    if not phone.startswith("whatsapp:"):
        phone = f"whatsapp:{phone}"
    return phone


def send_whatsapp_message(to_phone: str, message: str) -> str:
    client = get_twilio_client()
    settings = get_settings()
    from_phone = settings.twilio_whatsapp_from or "whatsapp:+14155238886"

    result = client.messages.create(
        body=message,
        from_=from_phone,
        to=normalize_whatsapp_to(to_phone),
    )
    return result.sid