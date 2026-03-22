"""Gemini-backed plan generation via google-genai structured JSON output."""

from __future__ import annotations

import logging
from typing import Any

from google.genai import types
from pydantic import ValidationError

from app.constants import PLAN_SAFETY_NOTE
from app.schemas.plan import PlanRequest, PlanResponse
from app.services.gemini_common import (
    coerce_generated_json,
    gemini_model_name,
    gemini_thinking_config,
    make_gemini_client,
    timed_generate_content,
)

logger = logging.getLogger(__name__)

_SYSTEM_INSTRUCTION = """You are an ADHD-friendly execution coach. The user will describe a goal and constraints.
Respond with a single JSON object only (no markdown fences, no commentary) that matches the response schema exactly.
Use 2-4 steps in "steps". Each step needs string "id", "title", "description", integer "estimated_minutes" (>=1).
"tiny_first_step" must be a 2-minute style micro-action.
"implementation_intention" must be a concrete if/then pair.
Set "safety_note" to "" (empty string); the server attaches the real disclaimer.
Generate a fresh UUID string for "plan_id".
Respect horizon, available_minutes, and energy: low energy means shorter steps and gentler wording in titles/descriptions."""


def _format_user_request(request: PlanRequest) -> str:
    return (
        f"Goal: {request.goal}\n"
        f"Horizon: {request.horizon}\n"
        f"Available minutes: {request.available_minutes}\n"
        f"Energy: {request.energy}\n"
    )


def _coerce_plan_response(resp: Any) -> PlanResponse:
    return coerce_generated_json(resp, PlanResponse)


def _with_standard_safety_note(plan: PlanResponse) -> PlanResponse:
    return plan.model_copy(update={"safety_note": PLAN_SAFETY_NOTE})


def generate_plan(request: PlanRequest) -> PlanResponse:
    """
    Call Gemini with structured JSON output (response_schema=PlanResponse).
    On validation failure, one repair retry with the error message.
    """
    client = make_gemini_client()
    thinking = gemini_thinking_config()
    base_config = types.GenerateContentConfig(
        system_instruction=_SYSTEM_INSTRUCTION,
        response_mime_type="application/json",
        response_schema=PlanResponse,
        thinking_config=thinking,
    )

    user_text = _format_user_request(request)
    last_error: str | None = None

    for attempt in range(2):
        contents: str = user_text
        if last_error is not None:
            contents = (
                f"{user_text}\n\n"
                "The previous output failed validation. Fix it and return JSON only.\n"
                f"Validation error: {last_error}\n"
            )

        response = timed_generate_content(
            logger,
            client,
            feature="plan",
            model=gemini_model_name(),
            contents=contents,
            config=base_config,
            attempt=attempt + 1,
        )

        try:
            return _with_standard_safety_note(_coerce_plan_response(response))
        except (ValidationError, ValueError, TypeError) as e:
            last_error = str(e)[:800]
            logger.warning("gemini plan parse failed attempt %s: %s", attempt + 1, last_error)
        except Exception as e:
            last_error = str(e)[:800]
            logger.warning("gemini plan unexpected error attempt %s: %s", attempt + 1, last_error)

    raise ValueError("Gemini did not return a valid plan after retries")
