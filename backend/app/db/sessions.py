from __future__ import annotations

from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.constants import SESSIONS_COLLECTION


async def insert_session_start(
    db: AsyncIOMotorDatabase, task_id: str, started_at: datetime
) -> None:
    """task_id is the plan_id for MVP (see app.constants)."""
    now = datetime.now(UTC)
    await db[SESSIONS_COLLECTION].insert_one(
        {
            "task_id": task_id,
            "plan_id": task_id,
            "started_at": started_at,
            "ended_at": None,
            "reflection": None,
            "created_at": now,
        }
    )


async def complete_session(
    db: AsyncIOMotorDatabase,
    task_id: str,
    ended_at: datetime,
    reflection: str,
) -> int:
    """
    Close the latest open session for this task_id (ended_at is null).
    Returns modified_count.
    """
    coll = db[SESSIONS_COLLECTION]
    doc = await coll.find_one(
        {"task_id": task_id, "ended_at": None},
        sort=[("started_at", -1)],
    )
    if doc is None:
        return 0
    result = await coll.update_one(
        {"_id": doc["_id"]},
        {"$set": {"ended_at": ended_at, "reflection": reflection}},
    )
    return result.modified_count
