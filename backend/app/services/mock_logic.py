def handle_start(user_id: str) -> str:
    return (
        "Start here: open the document and write the title only. "
        "Ignore formatting for now."
    )


def handle_stuck(user_id: str) -> str:
    return (
        "Got you. Try this: write just ONE bullet point. "
        "Only 2 minutes."
    )


def handle_done(user_id: str) -> str:
    return "Nice. That counts."


def handle_unknown() -> str:
    return (
        "Just chat naturally — I'll ask when I'm ready to build your plan. "
        "Then reply BUILD (or YES / GO). "
        "Quick commands: START, STUCK, DONE."
    )
