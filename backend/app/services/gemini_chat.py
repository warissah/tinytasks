"""Single-turn chat coach: extracts draft PlanRequest fields and optional finalize prompt."""

from __future__ import annotations

import logging

from google.genai import types
from pydantic import ValidationError

from app.schemas.chat import ChatTurnLLMOut, DraftPlanFields
from app.services.gemini_common import (
    coerce_generated_json,
    gemini_model_name,
    gemini_thinking_config,
    make_gemini_client,
    timed_generate_content,
)

logger = logging.getLogger(__name__)

_SYSTEM = """You are an ADHD-friendly execution coach. The user messages are free-form; you gently \
gather what you need to build a structured plan later.

Extract and maintain these fields (use null for unknown / not yet mentioned):
- draft_goal: concrete task they want to accomplish
- draft_horizon: today | week | long
- draft_available_minutes: how much time they can spend (5–1440); if they want shorter tasks or less time, \
use a smaller number
- draft_energy: low | medium | high

Rules:
- Keep reply short (WhatsApp-friendly): at most ~6 short lines.
- ask_finalize: set true only when draft_goal is clear enough to plan (specific enough to break into steps). \
When true, your reply MUST explicitly ask if they are ready for you to build their plan (e.g. "Ready for me to \
build your plan? Reply BUILD when you are.").
- Never claim you already built the plan; the server builds it on a separate finalize step.
- Output a single JSON object only (no markdown)."""


def _stub_turn(user_text: str, draft: DraftPlanFields) -> ChatTurnLLMOut:
    g = (draft.goal or user_text).strip() or user_text.strip()
    merged = draft.model_copy(update={"goal": g[:500]})
    ready = len(merged.goal.strip()) >= 8
    return ChatTurnLLMOut(
        reply=(
            "Tell me what you want to get done and about how much time you have. "
            "When it feels clear, say you're ready to build your plan."
            if not ready
            else "Sounds good. Ready for me to build your plan? Reply BUILD when you are."
        ),
        draft_goal=merged.goal if merged.goal else None,
        draft_horizon=None,
        draft_available_minutes=None,
        draft_energy=None,
        ask_finalize=ready,
    )


def _format_prompt(*, transcript: str, draft: DraftPlanFields, latest_user: str) -> str:
    return (
        f"Current draft (JSON): {draft.model_dump_json()}\n\n"
        f"Conversation so far:\n{transcript}\n\n"
        f"Latest user message:\n{latest_user}\n"
    )


def generate_chat_turn(*, transcript: str, draft: DraftPlanFields, latest_user: str) -> ChatTurnLLMOut:
    try:
        client = make_gemini_client()
    except RuntimeError:
        return _stub_turn(latest_user, draft)

    thinking = gemini_thinking_config()
    base_config = types.GenerateContentConfig(
        system_instruction=_SYSTEM,
        response_mime_type="application/json",
        response_schema=ChatTurnLLMOut,
        thinking_config=thinking,
    )
    user_block = _format_prompt(transcript=transcript, draft=draft, latest_user=latest_user)
    last_error: str | None = None

    for attempt in range(2):
        contents = user_block
        if last_error is not None:
            contents = (
                f"{user_block}\n\n"
                "Previous JSON failed validation. Return valid JSON only.\n"
                f"Error: {last_error}\n"
            )
        try:
            response = timed_generate_content(
                logger,
                client,
                feature="chat",
                model=gemini_model_name(),
                contents=contents,
                config=base_config,
                attempt=attempt + 1,
            )
            return coerce_generated_json(response, ChatTurnLLMOut)
        except (ValidationError, ValueError, TypeError) as e:
            last_error = str(e)[:800]
            logger.warning("gemini chat parse failed attempt %s: %s", attempt + 1, last_error)
        except Exception as e:
            last_error = str(e)[:800]
            logger.warning("gemini chat error attempt %s: %s", attempt + 1, last_error)

    logger.warning("gemini chat falling back to stub after retries")
    return _stub_turn(latest_user, draft)


def apply_llm_draft(base: DraftPlanFields, out: ChatTurnLLMOut) -> DraftPlanFields:
    data = base.model_dump()
    if out.draft_goal is not None:
        data["goal"] = out.draft_goal
    if out.draft_horizon is not None:
        data["horizon"] = out.draft_horizon
    if out.draft_available_minutes is not None:
        data["available_minutes"] = out.draft_available_minutes
    if out.draft_energy is not None:
        data["energy"] = out.draft_energy
    return DraftPlanFields.model_validate(data)
