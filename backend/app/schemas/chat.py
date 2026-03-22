"""Chat-before-plan: free-form turns extract a draft PlanRequest; finalize calls the same generator as POST /plan."""

from typing import Literal

from pydantic import BaseModel, Field

class DraftPlanFields(BaseModel):
    """Accumulated intent for a future PlanRequest (defaults match PlanRequest)."""

    goal: str = ""
    horizon: Literal["today", "week", "long"] = "today"
    available_minutes: int = Field(60, ge=5, le=24 * 60)
    energy: Literal["low", "medium", "high"] = "medium"


class ChatTurnLLMOut(BaseModel):
    """Structured Gemini output for one coach turn."""

    reply: str = Field(..., description="Short, warm reply to the user (plain text).")
    draft_goal: str | None = None
    draft_horizon: Literal["today", "week", "long"] | None = None
    draft_available_minutes: int | None = Field(default=None, ge=5, le=24 * 60)
    draft_energy: Literal["low", "medium", "high"] | None = None
    ask_finalize: bool = Field(
        False,
        description="True when enough is known to build a plan; reply should ask if they are ready.",
    )


class ChatMessageBody(BaseModel):
    thread_id: str | None = None
    text: str = Field(..., min_length=1, max_length=8000)


class ChatMessageResponse(BaseModel):
    thread_id: str
    reply: str
    draft: DraftPlanFields
    ask_finalize: bool


class ChatFinalizeBody(BaseModel):
    thread_id: str = Field(..., min_length=1)
