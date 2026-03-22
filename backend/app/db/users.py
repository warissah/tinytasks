from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.constants import USERS_COLLECTION
from app.services.user_identity import normalize_email, normalize_phone


def _now() -> datetime:
    return datetime.now(UTC)


async def get_user_by_id(
    db: AsyncIOMotorDatabase, user_id: str
) -> dict | None:
    return await db[USERS_COLLECTION].find_one({"user_id": user_id})


async def get_user_by_email(
    db: AsyncIOMotorDatabase, email: str | None
) -> dict | None:
    email_norm = normalize_email(email)
    if email_norm is None:
        return None
    return await db[USERS_COLLECTION].find_one({"email_normalized": email_norm})


async def get_user_by_phone(
    db: AsyncIOMotorDatabase, phone: str | None
) -> dict | None:
    phone_norm = normalize_phone(phone)
    if phone_norm is None:
        return None
    return await db[USERS_COLLECTION].find_one({"phone_normalized": phone_norm})


async def get_user_id_for_phone(
    db: AsyncIOMotorDatabase | None, phone: str | None
) -> str | None:
    if db is None:
        return None
    doc = await get_user_by_phone(db, phone)
    if doc is None:
        return None
    user_id = doc.get("user_id")
    if not user_id:
        return None
    return str(user_id)


async def create_or_reuse_guest_user(
    db: AsyncIOMotorDatabase,
    *,
    email: str,
    phone: str,
) -> tuple[dict, bool]:
    email_norm = normalize_email(email)
    phone_norm = normalize_phone(phone)
    if email_norm is None or phone_norm is None:
        raise ValueError("A valid email and phone are required")

    by_email = await get_user_by_email(db, email_norm)
    by_phone = await get_user_by_phone(db, phone_norm)

    if by_email is not None and by_phone is not None and by_email.get("user_id") != by_phone.get("user_id"):
        raise RuntimeError("contact_conflict")

    existing = by_email or by_phone
    now = _now()

    if existing is not None:
        await db[USERS_COLLECTION].update_one(
            {"_id": existing["_id"]},
            {
                "$set": {
                    "email": email.strip(),
                    "email_normalized": email_norm,
                    "phone": phone_norm,
                    "phone_normalized": phone_norm,
                    "updated_at": now,
                }
            },
        )
        existing["email"] = email.strip()
        existing["email_normalized"] = email_norm
        existing["phone"] = phone_norm
        existing["phone_normalized"] = phone_norm
        existing["updated_at"] = now
        return existing, False

    doc = {
        "user_id": str(uuid4()),
        "email": email.strip(),
        "email_normalized": email_norm,
        "phone": phone_norm,
        "phone_normalized": phone_norm,
        "created_at": now,
        "updated_at": now,
    }
    await db[USERS_COLLECTION].insert_one(doc)
    return doc, True
