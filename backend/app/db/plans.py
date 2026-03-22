from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

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


async def get_plan_by_plan_id(
    db: AsyncIOMotorDatabase, plan_id: str
) -> dict[str, Any] | None:
    return await db[PLANS_COLLECTION].find_one({"plan_id": plan_id})


async def update_plan_fields(
    db: AsyncIOMotorDatabase, plan_id: str, fields: dict[str, Any]
) -> None:
    if not fields:
        return
    await db[PLANS_COLLECTION].update_one({"plan_id": plan_id}, {"$set": fields})


def plan_response_from_doc(doc: dict[str, Any]) -> PlanResponse:
    raw = doc.get("plan")
    if raw is None:
        raise ValueError("plan document missing embedded 'plan'")
    return PlanResponse.model_validate(raw)
