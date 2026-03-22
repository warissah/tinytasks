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
            message="Stub nudge: take one tiny 2-minute action. Momentum beats motivation.",
            two_minute_action="Open the doc and change one line (any line).",
        )
    try:
        return gemini_generate_nudge(body)
    except Exception:
        logger.exception("Gemini nudge failed; falling back to stub")
        return NudgeResponse(
            message="Stub nudge: take one tiny 2-minute action. Momentum beats motivation.",
            two_minute_action="Open the doc and change one line (any line).",
        )
