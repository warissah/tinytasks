import logging

from fastapi import APIRouter, Request

from app.config import get_settings
from app.db.plans import insert_plan
from app.schemas.plan import PlanRequest, PlanResponse
from app.services.gemini_plan import generate_plan as gemini_generate_plan
from app.services.mock_plan import build_stub_plan

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=PlanResponse)
async def create_plan(request: Request, body: PlanRequest) -> PlanResponse:
    """Uses Gemini when GEMINI_API_KEY is set; otherwise returns the deterministic stub."""
    settings = get_settings()
    if not settings.gemini_api_key:
        response = build_stub_plan(body.goal)
    else:
        try:
            response = gemini_generate_plan(body)
        except Exception:
            logger.exception("Gemini plan generation failed; falling back to stub")
            response = build_stub_plan(body.goal)

    db = getattr(request.app.state, "mongo_db", None)
    if db is not None:
        try:
            await insert_plan(
                db,
                body.goal,
                response,
                user_phone=body.phone,
                user_id=body.user_id,
            )
        except Exception:
            logger.exception("Failed to persist plan to Mongo")

    return response
