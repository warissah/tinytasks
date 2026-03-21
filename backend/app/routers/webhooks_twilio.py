from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/twilio")
async def twilio_whatsapp(request: Request) -> dict[str, str]:
    """
    Stub inbound WhatsApp webhook.
    Twilio sends `application/x-www-form-urlencoded` — parse `From`, `Body`, etc. in T3.
    """
    form = await request.form()
    return {
        "status": "stub",
        "from": str(form.get("From", "")),
        "body": str(form.get("Body", "")),
    }
