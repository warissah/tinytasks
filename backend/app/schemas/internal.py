from typing import Literal

from pydantic import BaseModel, Field


class ReminderFireBody(BaseModel):
    user_id: str = Field(..., min_length=1)
    task_id: str = Field(..., min_length=1)
    reminder_kind: Literal["check_in_15m"] = "check_in_15m"


class ReminderFireResponse(BaseModel):
    status: Literal["sent", "skipped", "queued_stub"]
    detail: str
