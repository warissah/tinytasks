def parse_command(body: str) -> str:
    text = (body or "").strip().lower()

    if "start" in text:
        return "start"
    if "stuck" in text:
        return "stuck"
    if "done" in text:
        return "done"
    if "plan" in text:  
        return "plan"

    return "unknown"