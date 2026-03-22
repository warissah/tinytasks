import re

_FINALIZE = frozenset(
    {
        "build",
        "finalize",
        "yes",
        "y",
        "go",
        "ok",
        "replan",
    }
)


def parse_command(body: str) -> str:
    text = (body or "").strip()
    if not text:
        return "unknown"
    lowered = text.lower().rstrip(".!?")
    # Whole-message triggers only so we do not misfire on "yesterday" or "ok cool".
    if lowered in _FINALIZE:
        return "finalize"
    # Leading token for start/plan; word boundaries for stuck/done (avoid starting/planning → plan).
    if re.search(r"(?i)^\s*start\b", text):
        return "start"
    if re.search(r"(?i)^\s*plan\b", text):
        return "plan"
    if re.search(r"(?i)\bstuck\b", text):
        return "stuck"
    if re.search(r"(?i)\bdone\b", text):
        return "done"

    return "unknown"