from __future__ import annotations

from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.constants import PLANS_COLLECTION
from app.schemas.plan import PlanResponse


async def insert_plan(db: AsyncIOMotorDatabase, goal: str, plan: PlanResponse) -> None:
    doc = {
        "plan_id": plan.plan_id,
        "goal": goal,
        "plan": plan.model_dump(mode="json"),
        "created_at": datetime.now(UTC),
    }
    await db[PLANS_COLLECTION].insert_one(doc)
