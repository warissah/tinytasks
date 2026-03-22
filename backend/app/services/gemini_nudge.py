"""Gemini-backed /nudge: short re-entry coaching (structured JSON)."""

from __future__ import annotations

import logging
from typing import Any

from google.genai import types
from pydantic import ValidationError

from app.schemas.nudge import NudgeRequest, NudgeResponse
from app.services.gemini_common import (
    coerce_generated_json,
    gemini_model_name,
    gemini_thinking_config,
    make_gemini_client,
    timed_generate_content,
)

logger = logging.getLogger(__name__)

_SYSTEM_INSTRUCTION = """You are an ADHD-friendly execution coach. The user is stuck or needs a gentle push on an existing task.
Respond with a single JSON object only (no markdown fences, no commentary) matching the response schema exactly.

Fields:
- "nudge_type": one of "reentry", "encourage", "clarify". Use "reentry" for getting back on track; "encourage" if they sound discouraged; "clarify" if the block seems fuzzy or they need a smaller next question.
- "message": 1-3 short sentences, warm and practical, not clinical.
- "two_minute_action": one concrete micro-step they can do in about two minutes (specific, not vague).

Do not invent a full task list or plan; only this nudge."""


def _format_user_request(request: NudgeRequest) -> str:
    lines = [
        f"Task id: {request.task_id}",
        f"Context / what they're stuck on: {request.context or '(none)'}",
    ]
    if request.last_step_id:
        lines.append(f"Last step id they were on: {request.last_step_id}")
    return "\n".join(lines)


def _coerce_nudge_response(resp: Any) -> NudgeResponse:
    return coerce_generated_json(resp, NudgeResponse)


def generate_nudge(request: NudgeRequest) -> NudgeResponse:
    """Structured JSON nudge; one repair retry on validation failure."""
    client = make_gemini_client()
    thinking = gemini_thinking_config()
    base_config = types.GenerateContentConfig(
        system_instruction=_SYSTEM_INSTRUCTION,
        response_mime_type="application/json",
        response_schema=NudgeResponse,
        thinking_config=thinking,
    )

    user_text = _format_user_request(request)
    last_error: str | None = None

    for attempt in range(2):
        contents = user_text
        if last_error is not None:
            contents = (
                f"{user_text}\n\n"
                "The previous output failed validation. Fix it and return JSON only.\n"
                f"Validation error: {last_error}\n"
            )

        response = timed_generate_content(
            logger,
            client,
            feature="nudge",
            model=gemini_model_name(),
            contents=contents,
            config=base_config,
            attempt=attempt + 1,
        )

        try:
            return _coerce_nudge_response(response)
        except (ValidationError, ValueError, TypeError) as e:
            last_error = str(e)[:800]
            logger.warning("gemini nudge parse failed attempt %s: %s", attempt + 1, last_error)
        except Exception as e:
            last_error = str(e)[:800]
            logger.warning("gemini nudge unexpected error attempt %s: %s", attempt + 1, last_error)

    raise ValueError("Gemini did not return a valid nudge after retries")
