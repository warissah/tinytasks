from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SessionStartBody(BaseModel):
    task_id: str = Field(..., min_length=1)
    started_at: datetime


class SessionEndBody(BaseModel):
    task_id: str = Field(..., min_length=1)
    ended_at: datetime
    reflection: Literal["done", "blocked", "partial"]
