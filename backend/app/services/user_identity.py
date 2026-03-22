from __future__ import annotations

import re


def normalize_email(value: str | None) -> str | None:
    raw = (value or "").strip().lower()
    if not raw:
        return None
    if "@" not in raw or raw.startswith("@") or raw.endswith("@"):
        return None
    return raw


def normalize_phone(value: str | None) -> str | None:
    raw = (value or "").strip()
    if not raw:
        return None
    if raw.startswith("whatsapp:"):
        raw = raw[len("whatsapp:") :]
    raw = raw.strip()
    has_plus = raw.startswith("+")
    digits = re.sub(r"\D", "", raw)
    if len(digits) < 7:
        return None
    if has_plus:
        return f"+{digits}"
    return f"+{digits}"
