from fastapi import APIRouter, Header, HTTPException, status

from app.config import get_settings
from app.schemas.internal import ReminderFireBody, ReminderFireResponse

router = APIRouter()


@router.post("/reminders/fire", response_model=ReminderFireResponse)
def fire_reminder(
    body: ReminderFireBody,
    x_internal_key: str | None = Header(default=None, alias="X-Internal-Key"),
) -> ReminderFireResponse:
    """
    Fetch.ai (or other internal automation) calls this endpoint.
    Stub: validates secret only — Twilio send comes later (T3/T4).
    """
    settings = get_settings()
    if not settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="INTERNAL_API_KEY is not set on the server",
        )
    if x_internal_key != settings.internal_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal key")

    return ReminderFireResponse(
        status="queued_stub",
        detail=(
            f"Would send reminder={body.reminder_kind} for user={body.user_id} "
            f"task={body.task_id} (wire Twilio outbound next)"
        ),
    )
