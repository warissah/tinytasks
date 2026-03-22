from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "adhd-coach-api"
    debug: bool = True

    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"

    # Required for POST /internal/reminders/fire in production; stub allows missing for local dev
    internal_api_key: str | None = None

    # MongoDB Atlas — mongodb+srv://... (DB name in path, or set mongodb_database)
    mongodb_uri: str | None = None
    mongodb_database: str | None = None

    # Google Gen AI (Gemini) — used by google-genai SDK; optional until routes call the model
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3-flash-preview"
    # Gemini 3: minimal/low/medium/high — omit or leave unset to use API default (often lowest latency).
    gemini_thinking_level: Literal["minimal", "low", "medium", "high"] | None = None
    # Log wall-clock ms per generate_content call (model, thinking_level, attempt) for latency experiments
    gemini_log_timing: bool = True

    # Twilio WhatsApp (T3 coordinates console; values live on server env in prod)
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_whatsapp_from: str | None = None
    # Hackathon fallback: when user_id is not a phone and no Mongo row in user_whatsapp, send here
    # (e.g. whatsapp:+15551234567). Still useful for demos after user_whatsapp exists.
    reminder_demo_whatsapp_to: str | None = None

    # Hackathon fallback when Mongo is unavailable during onboarding
    demo_user_id: str | None = None
    demo_user_email: str | None = None
    demo_user_phone: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


def cors_origin_list() -> list[str]:
    raw = getattr(get_settings(), "cors_origins", None) or ""
    return [o.strip() for o in raw.split(",") if o.strip()]
