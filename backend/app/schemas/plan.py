from typing import Literal

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    goal: str = Field(..., min_length=1)
    horizon: Literal["today", "week", "long"] = "today"
    available_minutes: int = Field(60, ge=5, le=24 * 60)
    energy: Literal["low", "medium", "high"] = "medium"
    user_id: str | None = None
    # Optional E.164 (same string Twilio uses after stripping whatsapp:). Links web plan to WhatsApp STUCK/nudge.
    phone: str | None = None


class SuggestedWindow(BaseModel):
    label: str | None = None
    start: str | None = None
    end: str | None = None


class PlanStep(BaseModel):
    id: str
    title: str
    description: str
    estimated_minutes: int = Field(..., ge=1)
    suggested_window: SuggestedWindow | None = None


class TinyFirstStep(BaseModel):
    title: str
    description: str
    estimated_minutes: int = Field(..., ge=1)


class ImplementationIntention(BaseModel):
    if_condition: str
    then_action: str


class PlanResponse(BaseModel):
    plan_id: str
    summary: str
    tiny_first_step: TinyFirstStep
    steps: list[PlanStep]
    implementation_intention: ImplementationIntention
    # Default lets Gemini send ""; API layer replaces with PLAN_SAFETY_NOTE for real responses.
    safety_note: str = Field(
        default="",
        description="Server fills with standard disclaimer; model may omit or use empty string.",
    )
