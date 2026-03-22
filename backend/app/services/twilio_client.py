from twilio.rest import Client

from app.config import get_settings


def send_whatsapp_message(to_number: str, body: str) -> str:
    settings = get_settings()
    sid = settings.twilio_account_sid
    token = settings.twilio_auth_token
    if not sid or not token:
        raise RuntimeError("Missing Twilio credentials")

    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"

    from_number = settings.twilio_whatsapp_from or "whatsapp:+14155238886"

    client = Client(sid, token)
    message = client.messages.create(
        from_=from_number,
        to=to_number,
        body=body,
    )
    return message.sid