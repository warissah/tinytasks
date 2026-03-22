"""GET /demo/events — polled by the frontend to sync WhatsApp actions to the web app."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/events")
async def get_demo_events(request: Request, since: float | None = None) -> dict[str, Any]:
    db = getattr(request.app.state, "mongo_db", None)
    if db is None:
        return {"events": []}
    from app.db.demo_events import get_events_since
    events = await get_events_since(db, since)
    return {"events": events}
