"""
Pytest loads `conftest.py` before test modules — set env here so `app.main` imports cleanly.
"""

import os

# Ensure internal routes are enabled during tests (never use real secrets in repo).
os.environ.setdefault("INTERNAL_API_KEY", "test-internal-key")

import pytest

from app.config import get_settings


@pytest.fixture(autouse=True)
def reset_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
