from fastapi import APIRouter

from app.schemas.plan import PlanRequest, PlanResponse
from app.services.mock_plan import build_stub_plan

router = APIRouter()


@router.post("", response_model=PlanResponse)
def create_plan(body: PlanRequest) -> PlanResponse:
    """Stub implementation: replace `build_stub_plan` with Gemini + validation."""
    return build_stub_plan(body.goal)
