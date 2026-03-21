from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "adhd-coach-api"
    debug: bool = True

    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"

    # Required for POST /internal/reminders/fire in production; stub allows missing for local dev
    internal_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


def cors_origin_list() -> list[str]:
    return [o.strip() for o in get_settings().cors_origins.split(",") if o.strip()]
