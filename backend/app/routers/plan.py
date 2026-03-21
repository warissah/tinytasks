import logging

from fastapi import APIRouter

from app.config import get_settings
from app.schemas.plan import PlanRequest, PlanResponse
from app.services.gemini_plan import generate_plan as gemini_generate_plan
from app.services.mock_plan import build_stub_plan

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=PlanResponse)
def create_plan(body: PlanRequest) -> PlanResponse:
    """Uses Gemini when GEMINI_API_KEY is set; otherwise returns the deterministic stub."""
    settings = get_settings()
    if not settings.gemini_api_key:
        return build_stub_plan(body.goal)
    try:
        return gemini_generate_plan(body)
    except Exception:
        logger.exception("Gemini plan generation failed; falling back to stub")
        return build_stub_plan(body.goal)
