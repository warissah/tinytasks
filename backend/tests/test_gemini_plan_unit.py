"""Unit tests for Gemini plan helpers (no network)."""

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from google.genai import types

import app.services.gemini_common as gemini_common_mod
from app.constants import PLAN_SAFETY_NOTE
from app.schemas.plan import PlanResponse
from app.services.gemini_common import gemini_thinking_config, strip_json_fence
from app.services.gemini_plan import _coerce_plan_response, _with_standard_safety_note


def test_strip_json_fence() -> None:
    raw = '{"a": 1}'
    assert strip_json_fence(f"```json\n{raw}\n```") == raw
    assert strip_json_fence(raw) == raw


_VALID_MINIMAL = (
    '{"plan_id":"p1","summary":"s","tiny_first_step":{"title":"t","description":"d","estimated_minutes":2},'
    '"steps":[{"id":"1","title":"a","description":"b","estimated_minutes":5}],'
    '"implementation_intention":{"if_condition":"x","then_action":"y"},'
    '"safety_note":"Non-clinical. 988."}'
)


def test_coerce_from_parsed_dict() -> None:
    data = PlanResponse.model_validate_json(_VALID_MINIMAL).model_dump()
    resp = SimpleNamespace(parsed=data, text=None)
    out = _coerce_plan_response(resp)
    assert out.plan_id == "p1"


def test_coerce_from_text() -> None:
    resp = SimpleNamespace(parsed=None, text=_VALID_MINIMAL)
    out = _coerce_plan_response(resp)
    assert out.summary == "s"


def test_with_standard_safety_note_overwrites() -> None:
    resp = SimpleNamespace(parsed=None, text=_VALID_MINIMAL)
    raw = _coerce_plan_response(resp)
    assert raw.safety_note == "Non-clinical. 988."
    fixed = _with_standard_safety_note(raw)
    assert fixed.safety_note == PLAN_SAFETY_NOTE


def test_coerce_invalid_raises() -> None:
    resp = SimpleNamespace(parsed=None, text='{"plan_id": "x"}')
    with pytest.raises(ValidationError):
        _coerce_plan_response(resp)


def test_thinking_config_none_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        gemini_common_mod,
        "get_settings",
        lambda: SimpleNamespace(gemini_thinking_level=None),
    )
    assert gemini_thinking_config() is None


def test_thinking_config_minimal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        gemini_common_mod,
        "get_settings",
        lambda: SimpleNamespace(gemini_thinking_level="minimal"),
    )
    tc = gemini_thinking_config()
    assert tc is not None
    assert tc.thinking_level == types.ThinkingLevel.MINIMAL
