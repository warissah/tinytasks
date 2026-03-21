from fastapi import APIRouter

from app.schemas.nudge import NudgeRequest, NudgeResponse

router = APIRouter()


@router.post("", response_model=NudgeResponse)
def nudge(body: NudgeRequest) -> NudgeResponse:
    """Stub: wire to Gemini for empathetic re-entry prompts."""
    return NudgeResponse(
        message="Stub nudge: take one tiny 2-minute action. Momentum beats motivation.",
        two_minute_action="Open the doc and change one line (any line).",
    )
