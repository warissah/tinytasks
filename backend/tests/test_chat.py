import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_chat_message_creates_thread() -> None:
    res = client.post("/chat/message", json={"text": "I need to finish my essay tonight"})
    assert res.status_code == 200
    data = res.json()
    assert "thread_id" in data
    assert data["reply"]
    assert "draft" in data
    assert "ask_finalize" in data


@pytest.mark.integration
def test_chat_finalize_requires_goal() -> None:
    res = client.post("/chat/message", json={"text": "hi"})
    tid = res.json()["thread_id"]
    fin = client.post("/chat/finalize", json={"thread_id": tid})
    assert fin.status_code == 400


@pytest.mark.integration
def test_chat_roundtrip_finalize() -> None:
    r1 = client.post(
        "/chat/message",
        json={"text": "I want to clean my desk, I have 20 minutes and low energy"},
    )
    assert r1.status_code == 200
    tid = r1.json()["thread_id"]
    fin = client.post("/chat/finalize", json={"thread_id": tid})
    assert fin.status_code == 200
    plan = fin.json()
    assert plan.get("plan_id")
    assert plan.get("tiny_first_step")


@pytest.mark.integration
def test_parse_finalize_keywords() -> None:
    from app.services.command_parser import parse_command

    assert parse_command("BUILD") == "finalize"
    assert parse_command("yes") == "finalize"
    assert parse_command("ok") == "finalize"
    assert parse_command("ok cool") == "unknown"
