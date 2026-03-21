"""Gemini-backed plan generation via google-genai structured JSON output."""

from __future__ import annotations

import logging
import re
import time
from typing import Any

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.config import get_settings
from app.constants import PLAN_SAFETY_NOTE
from app.schemas.plan import PlanRequest, PlanResponse

logger = logging.getLogger(__name__)

_SYSTEM_INSTRUCTION = """You are an ADHD-friendly execution coach. The user will describe a goal and constraints.
Respond with a single JSON object only (no markdown fences, no commentary) that matches the response schema exactly.
Use 2-4 steps in "steps". Each step needs string "id", "title", "description", integer "estimated_minutes" (>=1).
"tiny_first_step" must be a 2-minute style micro-action.
"implementation_intention" must be a concrete if/then pair.
Set "safety_note" to "" (empty string); the server attaches the real disclaimer.
Generate a fresh UUID string for "plan_id".
Respect horizon, available_minutes, and energy: low energy means shorter steps and gentler wording in titles/descriptions."""


def _model_name() -> str:
    return get_settings().gemini_model


def _thinking_config() -> types.ThinkingConfig | None:
    """Map GEMINI_THINKING_LEVEL to SDK enum; None = leave model default (good for latency A/B)."""
    raw = get_settings().gemini_thinking_level
    if raw is None:
        return None
    level_map = {
        "minimal": types.ThinkingLevel.MINIMAL,
        "low": types.ThinkingLevel.LOW,
        "medium": types.ThinkingLevel.MEDIUM,
        "high": types.ThinkingLevel.HIGH,
    }
    return types.ThinkingConfig(thinking_level=level_map[raw])


def _format_user_request(request: PlanRequest) -> str:
    return (
        f"Goal: {request.goal}\n"
        f"Horizon: {request.horizon}\n"
        f"Available minutes: {request.available_minutes}\n"
        f"Energy: {request.energy}\n"
    )


def _strip_json_fence(text: str) -> str:
    t = text.strip()
    m = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", t, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else t


def _coerce_plan_response(resp: Any) -> PlanResponse:
    """Turn a generate_content response into PlanResponse."""
    parsed = getattr(resp, "parsed", None)
    if parsed is not None:
        if isinstance(parsed, PlanResponse):
            return parsed
        return PlanResponse.model_validate(parsed)

    raw = _strip_json_fence(getattr(resp, "text", None) or "")
    if not raw:
        raise ValueError("empty model response")
    return PlanResponse.model_validate_json(raw)


def _with_standard_safety_note(plan: PlanResponse) -> PlanResponse:
    return plan.model_copy(update={"safety_note": PLAN_SAFETY_NOTE})


def generate_plan(request: PlanRequest) -> PlanResponse:
    """
    Call Gemini with structured JSON output (response_schema=PlanResponse).
    On validation failure, one repair retry with the error message.
    """
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=settings.gemini_api_key)
    thinking = _thinking_config()
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

        t0 = time.perf_counter()
        response = client.models.generate_content(
            model=_model_name(),
            contents=contents,
            config=base_config,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if settings.gemini_log_timing:
            logger.info(
                "gemini generate_content model=%s thinking_level=%s attempt=%s elapsed_ms=%.1f",
                _model_name(),
                settings.gemini_thinking_level or "default",
                attempt + 1,
                elapsed_ms,
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
