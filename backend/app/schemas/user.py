from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CreateGuestUserRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=320)
    phone: str = Field(..., min_length=1, max_length=64)


class CreateGuestUserResponse(BaseModel):
    user_id: str
    email: str
    phone: str
    is_new_user: bool
    persistence: Literal["mongo", "demo_fallback"]
