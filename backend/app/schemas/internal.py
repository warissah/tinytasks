from typing import Literal

from pydantic import BaseModel, Field


class AgentCallbackContext(BaseModel):
    """
    Optional metadata from the Fetch uAgent (strong integration story).

    TODO: /internal/reminders/fire does not yet persist or branch on these fields — see router module docstring.
    Intended: energy_hint + Gemini tone; push_back_start_minutes → next_reminder_at in Mongo;
    replan_intensity smaller_steps|lighter → Gemini replan + persist plan.
    """

    energy_hint: Literal["unknown", "low", "medium", "high"] | None = None
    push_back_start_minutes: int | None = Field(
        default=None,
        ge=0,
        le=24 * 60,
        description="Delay next actionable nudge by this many minutes (persist next_reminder_at).",
    )
    replan_intensity: Literal["same", "smaller_steps", "lighter"] | None = Field(
        default=None,
        description="If smaller_steps/lighter, backend may call Gemini to shrink the plan.",
    )


class ReminderFireBody(BaseModel):
    user_id: str = Field(..., min_length=1)
    task_id: str = Field(..., min_length=1)
    reminder_kind: Literal["check_in_15m"] = "check_in_15m"
    agent_context: AgentCallbackContext | None = None


class ReminderFireResponse(BaseModel):
    status: Literal["sent", "skipped", "failed"]
    detail: str
