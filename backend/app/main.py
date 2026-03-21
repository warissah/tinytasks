from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import cors_origin_list, get_settings
from app.routers import health, internal_reminders, nudge, plan, session, webhooks_twilio


def create_app() -> FastAPI:
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
