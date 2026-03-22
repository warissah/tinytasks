"""Re-plan an existing PlanResponse (smaller steps or lighter tone) via Gemini or stub."""

from __future__ import annotations

import json
import logging
from typing import Literal

from google.genai import types
from pydantic import ValidationError

from app.constants import PLAN_SAFETY_NOTE
from app.schemas.plan import PlanResponse
from app.services.gemini_common import (
    coerce_generated_json,
    gemini_model_name,
    gemini_thinking_config,
    make_gemini_client,
    timed_generate_content,
)

logger = logging.getLogger(__name__)

ReplanIntensity = Literal["smaller_steps", "lighter"]

_SYSTEM = """You revise an existing ADHD coaching plan JSON. Return a single JSON object only (no markdown).
The output must match the PlanResponse schema exactly. Keep the SAME "plan_id" string as the input plan.
For "smaller_steps": fewer/shorter steps, lower estimated_minutes, a tinier first step.
For "lighter": keep structure but gentler, lower-pressure wording in titles/descriptions.
Set "safety_note" to "" (empty string); the server attaches the real disclaimer."""


def _with_safety(plan: PlanResponse) -> PlanResponse:
    return plan.model_copy(update={"safety_note": PLAN_SAFETY_NOTE})


def stub_replan(plan: PlanResponse, intensity: ReplanIntensity) -> PlanResponse:
    """Deterministic fallback when Gemini is off or fails. Preserves plan_id."""
    if intensity == "smaller_steps":
        new_steps = []
        for s in plan.steps[:2]:
            em = max(1, s.estimated_minutes // 2)
            new_steps.append(
                s.model_copy(
                    update={
                        "title": f"{s.title} (smaller slice)",
                        "description": s.description[:200],
                        "estimated_minutes": em,
                    }
                )
            )
        tfs = plan.tiny_first_step.model_copy(
            update={
                "title": f"{plan.tiny_first_step.title} (tiny)",
                "estimated_minutes": max(1, min(3, plan.tiny_first_step.estimated_minutes)),
            }
        )
        return plan.model_copy(
            update={
                "summary": f"{plan.summary} — taking smaller steps.",
                "tiny_first_step": tfs,
                "steps": new_steps,
            }
        )

    # lighter
    new_steps = [
        s.model_copy(
            update={
                "title": s.title.replace("must", "could").replace("Need", "Consider")[:120],
            }
        )
        for s in plan.steps
    ]
    return plan.model_copy(
        update={
            "summary": f"Gentler pace: {plan.summary[:200]}",
            "tiny_first_step": plan.tiny_first_step.model_copy(
                update={"title": f"Easy start: {plan.tiny_first_step.title[:80]}"}
            ),
            "steps": new_steps,
        }
    )


def _gemini_replan(
    plan: PlanResponse,
    intensity: ReplanIntensity,
    energy_hint: str | None,
) -> PlanResponse:
    client = make_gemini_client()
    thinking = gemini_thinking_config()
    base_config = types.GenerateContentConfig(
        system_instruction=_SYSTEM,
        response_mime_type="application/json",
        response_schema=PlanResponse,
        thinking_config=thinking,
    )
    payload = {
        "existing_plan": plan.model_dump(mode="json"),
        "replan_intensity": intensity,
        "energy_hint": energy_hint,
    }
    user_text = json.dumps(payload, ensure_ascii=False)
    last_error: str | None = None

    for attempt in range(2):
        contents = user_text
        if last_error is not None:
            contents = (
                f"{user_text}\n\n"
                "Previous output failed validation. Fix JSON only.\n"
                f"Validation error: {last_error}\n"
            )
        response = timed_generate_content(
            logger,
            client,
            feature="replan",
            model=gemini_model_name(),
            contents=contents,
            config=base_config,
            attempt=attempt + 1,
        )
        try:
            out = coerce_generated_json(response, PlanResponse)
            if out.plan_id != plan.plan_id:
                out = out.model_copy(update={"plan_id": plan.plan_id})
            return _with_safety(out)
        except (ValidationError, ValueError, TypeError) as e:
            last_error = str(e)[:800]
            logger.warning("gemini replan parse failed attempt %s: %s", attempt + 1, last_error)

    raise ValueError("Gemini replan did not return valid JSON after retries")


def replan_existing(
    plan: PlanResponse,
    intensity: ReplanIntensity,
    energy_hint: str | None = None,
) -> PlanResponse:
    """Shrink or soften an existing plan; uses stub when GEMINI_API_KEY is missing."""
    from app.config import get_settings

    settings = get_settings()
    if not settings.gemini_api_key:
        return _with_safety(stub_replan(plan, intensity))
    try:
        return _gemini_replan(plan, intensity, energy_hint)
    except Exception:
        logger.exception("Gemini replan failed; using stub")
        return _with_safety(stub_replan(plan, intensity))
