from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.constants import PLANS_COLLECTION
from app.schemas.plan import PlanResponse


async def insert_plan(
    db: AsyncIOMotorDatabase,
    goal: str,
    plan: PlanResponse,
    *,
    user_phone: str | None = None,
    user_id: str | None = None,
) -> None:
    doc: dict[str, Any] = {
        "plan_id": plan.plan_id,
        "goal": goal,
        "plan": plan.model_dump(mode="json"),
        "created_at": datetime.now(UTC),
    }
    if user_phone and str(user_phone).strip():
        doc["user_phone"] = str(user_phone).strip()
    if user_id and str(user_id).strip():
        doc["user_id"] = str(user_id).strip()
    await db[PLANS_COLLECTION].insert_one(doc)


async def get_plan_by_plan_id(
    db: AsyncIOMotorDatabase, plan_id: str
) -> dict[str, Any] | None:
    return await db[PLANS_COLLECTION].find_one({"plan_id": plan_id})


async def find_latest_plan_id_for_phone(
    db: AsyncIOMotorDatabase, phone: str
) -> str | None:
    """Latest persisted plan for this phone (e.g. web POST /plan with phone set)."""
    phone = (phone or "").strip()
    if not phone:
        return None
    doc = await db[PLANS_COLLECTION].find_one(
        {"user_phone": phone},
        sort=[("created_at", -1)],
    )
    if doc is None:
        return None
    pid = doc.get("plan_id")
    return str(pid).strip() if pid else None


async def find_latest_plan_id_for_user_id(
    db: AsyncIOMotorDatabase, user_id: str
) -> str | None:
    user_id = (user_id or "").strip()
    if not user_id:
        return None
    doc = await db[PLANS_COLLECTION].find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)],
    )
    if doc is None:
        return None
    pid = doc.get("plan_id")
    return str(pid).strip() if pid else None


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
