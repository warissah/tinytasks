from typing import Literal

from pydantic import BaseModel, Field


class NudgeRequest(BaseModel):
    task_id: str = Field(..., min_length=1)
    context: str = ""
    last_step_id: str | None = None


class NudgeResponse(BaseModel):
    nudge_type: Literal["reentry", "encourage", "clarify"] = "reentry"
    message: str
    two_minute_action: str
