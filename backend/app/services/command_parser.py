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
    text = (body or "").strip().lower().rstrip(".!?")
    # Whole-message triggers only so we do not misfire on "yesterday" or "ok cool".
    if text in _FINALIZE:
        return "finalize"
    text_loose = (body or "").strip().lower()
    if "start" in text_loose:
        return "start"
    if "stuck" in text_loose:
        return "stuck"
    if "done" in text_loose:
        return "done"
    if "plan" in text:  
        return "plan"

    return "unknown"