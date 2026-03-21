import uuid

from app.constants import PLAN_SAFETY_NOTE
from app.schemas.plan import (
    ImplementationIntention,
    PlanResponse,
    PlanStep,
    SuggestedWindow,
    TinyFirstStep,
)


def build_stub_plan(goal: str) -> PlanResponse:
    """Deterministic stub until Gemini is wired. Keeps contract stable for frontend + tests."""
    pid = str(uuid.uuid4())
    return PlanResponse(
        plan_id=pid,
        summary=f"Stub plan for: {goal[:120]}",
        tiny_first_step=TinyFirstStep(
            title="Open your notes and write one sentence",
            description="No editing; one sentence only.",
            estimated_minutes=2,
        ),
        steps=[
            PlanStep(
                id="1",
                title="Brain dump",
                description="List bullet points for 10 minutes.",
                estimated_minutes=10,
                suggested_window=SuggestedWindow(
                    label="Next focus block",
                    start=None,
                    end=None,
                ),
            ),
            PlanStep(
                id="2",
                title="Pick the smallest next move",
                description="Choose one item you can finish in 15 minutes.",
                estimated_minutes=15,
                suggested_window=None,
            ),
        ],
        implementation_intention=ImplementationIntention(
            if_condition="When I open my laptop",
            then_action="I start a 5-minute timer and only do step 1",
        ),
        safety_note=PLAN_SAFETY_NOTE,
    )
