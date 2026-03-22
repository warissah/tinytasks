import logging

from fastapi import APIRouter

from app.config import get_settings
from app.schemas.nudge import NudgeRequest, NudgeResponse
from app.services.gemini_nudge import generate_nudge as gemini_generate_nudge

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=NudgeResponse)
def nudge(body: NudgeRequest) -> NudgeResponse:
    """Uses Gemini when GEMINI_API_KEY is set; otherwise deterministic stub."""
    settings = get_settings()
    if not settings.gemini_api_key:
        return NudgeResponse(
            nudge_type="reentry",
            message="You do not need to finish everything right now. Just restart with one tiny step.",
            two_minute_action="Open the task, spend 2 minutes on the easiest possible next action, then stop if you want.",
        )
    try:
        return gemini_generate_nudge(body)
    except Exception:
        logger.exception("Gemini nudge failed; falling back to stub")
        return NudgeResponse(
            nudge_type="reentry",
            message="You do not need to finish everything right now. Just restart with one tiny step.",
            two_minute_action="Open the task, spend 2 minutes on the easiest possible next action, then stop if you want.",
        )
