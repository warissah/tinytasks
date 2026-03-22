"""Optional Mongo mapping: app/Fetch user_id → WhatsApp destination for outbound reminders."""

from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.constants import USER_WHATSAPP_COLLECTION
from app.services.user_identity import normalize_phone


async def get_whatsapp_for_user_id(
    db: AsyncIOMotorDatabase, user_id: str
) -> str | None:
    """
    Return stored WhatsApp address for this user_id, or None.

    Document shape (insert via Atlas UI or script):
      { "user_id": "<same string as ReminderFireBody.user_id>", "whatsapp": "+15551234567" }
    ``whatsapp`` may include or omit the ``whatsapp:`` prefix; normalization happens in the router.
    """
    uid = (user_id or "").strip()
    if not uid:
        return None
    doc = await db[USER_WHATSAPP_COLLECTION].find_one({"user_id": uid})
    if doc is None:
        return None
    raw = doc.get("whatsapp") or doc.get("whatsapp_to")
    if raw is None or not str(raw).strip():
        return None
    return str(raw).strip()


async def upsert_whatsapp_for_user_id(
    db: AsyncIOMotorDatabase, user_id: str, phone: str | None
) -> None:
    uid = (user_id or "").strip()
    phone_norm = normalize_phone(phone)
    if not uid or phone_norm is None:
        return
    await db[USER_WHATSAPP_COLLECTION].update_one(
        {"user_id": uid},
        {"$set": {"user_id": uid, "whatsapp": phone_norm}},
        upsert=True,
    )
