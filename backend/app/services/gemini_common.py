"""Shared Gemini (google-genai) helpers for all feature modules (plan, nudge, …)."""

from __future__ import annotations

import logging
import re
import time
from typing import Any, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.config import get_settings

T = TypeVar("T", bound=BaseModel)


def strip_json_fence(text: str) -> str:
    """Remove optional ```json … ``` wrapping from model output."""
    t = text.strip()
    m = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", t, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else t


def gemini_model_name() -> str:
    return get_settings().gemini_model


def gemini_thinking_config() -> types.ThinkingConfig | None:
    """Map GEMINI_THINKING_LEVEL to SDK enum; None = API default (good for latency A/B)."""
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


def make_gemini_client() -> genai.Client:
    """Build a client; caller must ensure GEMINI_API_KEY is set."""
    key = get_settings().gemini_api_key
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    return genai.Client(api_key=key)


def coerce_generated_json(resp: Any, model_cls: type[T]) -> T:
    """Use SDK `parsed` when present, else parse `text` into a Pydantic model."""
    parsed = getattr(resp, "parsed", None)
    if parsed is not None:
        if isinstance(parsed, model_cls):
            return parsed
        return model_cls.model_validate(parsed)

    raw = strip_json_fence(getattr(resp, "text", None) or "")
    if not raw:
        raise ValueError("empty model response")
    return model_cls.model_validate_json(raw)


def log_generate_content_timing(
    logger: logging.Logger,
    settings: Any,
    *,
    feature: str,
    attempt: int,
    elapsed_ms: float,
) -> None:
    """Emit one INFO line for latency experiments (guarded by gemini_log_timing)."""
    if not settings.gemini_log_timing:
        return
    logger.info(
        "gemini %s generate_content model=%s thinking_level=%s attempt=%s elapsed_ms=%.1f",
        feature,
        settings.gemini_model,
        settings.gemini_thinking_level or "default",
        attempt,
        elapsed_ms,
    )


def timed_generate_content(
    logger: logging.Logger,
    client: genai.Client,
    *,
    feature: str,
    model: str,
    contents: str,
    config: types.GenerateContentConfig,
    attempt: int,
) -> Any:
    """Call generate_content and optionally log wall-clock ms."""
    settings = get_settings()
    t0 = time.perf_counter()
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    log_generate_content_timing(
        logger,
        settings,
        feature=feature,
        attempt=attempt,
        elapsed_ms=elapsed_ms,
    )
    return response


__all__ = [
    "coerce_generated_json",
    "gemini_model_name",
    "gemini_thinking_config",
    "log_generate_content_timing",
    "make_gemini_client",
    "strip_json_fence",
    "timed_generate_content",
]
