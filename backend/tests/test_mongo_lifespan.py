"""
Deployment-style checks: lifespan must not crash on common env mistakes.

CI/local tests usually omit MONGODB_URI, so Motor startup is skipped entirely.
Production often sets a placeholder or broken URI (e.g. mongodb:// with no host),
which used to raise during lifespan and kill the process.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_app_starts_when_mongodb_uri_is_invalid_placeholder(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MONGODB_URI", "mongodb://")
    monkeypatch.setenv("INTERNAL_API_KEY", "test-internal-key")

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application) as client:
        res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
