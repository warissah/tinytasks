"""Simple event bus for the hackathon demo — lets WhatsApp commands push state to the web app."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

COLLECTION = "demo_events"


async def insert_demo_event(db: AsyncIOMotorDatabase, event_type: str, data: dict[str, Any]) -> None:
    await db[COLLECTION].insert_one({
        "type": event_type,
        "data": data,
        "timestamp": datetime.now(UTC),
    })


async def get_events_since(db: AsyncIOMotorDatabase, since_ts: float | None = None) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if since_ts is not None:
        query["timestamp"] = {"$gt": datetime.fromtimestamp(since_ts, tz=UTC)}
    cursor = db[COLLECTION].find(query).sort("timestamp", 1).limit(50)
    events = []
    async for doc in cursor:
        events.append({
            "id": str(doc["_id"]),
            "type": doc["type"],
            "data": doc.get("data", {}),
            "timestamp": doc["timestamp"].timestamp(),
        })
    return events
