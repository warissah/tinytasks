import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import cors_origin_list, get_settings
from app.routers import health, internal_reminders, nudge, plan, session, webhooks_twilio

_GEMINI_LOG_HANDLER_MARKER = "_beachhacks_gemini_stderr"


def _configure_app_logging() -> None:
    """
    Uvicorn often leaves the root logger without a handler that receives app.* records.
    Attach a stderr StreamHandler directly to the Gemini module logger so timing INFO always shows.
    """
    root = logging.getLogger()
    if root.level == logging.NOTSET or root.level > logging.INFO:
        root.setLevel(logging.INFO)

    for name in ("app", "app.services", "app.services.gemini_plan"):
        logging.getLogger(name).setLevel(logging.INFO)

    gemini_log = logging.getLogger("app.services.gemini_plan")
    if not any(getattr(h, _GEMINI_LOG_HANDLER_MARKER, False) for h in gemini_log.handlers):
        h = logging.StreamHandler(sys.stderr)
        setattr(h, _GEMINI_LOG_HANDLER_MARKER, True)
        h.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
        gemini_log.addHandler(h)


def create_app() -> FastAPI:
    _configure_app_logging()
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origin_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(plan.router, prefix="/plan", tags=["plan"])
    app.include_router(nudge.router, prefix="/nudge", tags=["nudge"])
    app.include_router(session.router, prefix="/session", tags=["session"])
    app.include_router(internal_reminders.router, prefix="/internal", tags=["internal"])
    app.include_router(webhooks_twilio.router, prefix="/webhooks", tags=["webhooks"])

    return app


app = create_app()
