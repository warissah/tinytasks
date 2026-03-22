from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.constants import CHAT_THREADS_COLLECTION
from app.schemas.chat import DraftPlanFields

logger = logging.getLogger(__name__)

_MAX_MESSAGES = 32
_memory_lock = asyncio.Lock()
_memory_threads: dict[str, dict[str, Any]] = {}


def _now() -> datetime:
    return datetime.now(UTC)


def _new_doc(thread_id: str) -> dict[str, Any]:
    return {
        "thread_id": thread_id,
        "messages": [],
        "draft": DraftPlanFields().model_dump(),
        "created_at": _now(),
        "updated_at": _now(),
    }


async def _mem_get(thread_id: str) -> dict[str, Any] | None:
    async with _memory_lock:
        doc = _memory_threads.get(thread_id)
        if doc is None:
            return None
        return doc.copy()


async def _mem_put(doc: dict[str, Any]) -> None:
    async with _memory_lock:
        _memory_threads[doc["thread_id"]] = doc.copy()


async def create_thread(db: AsyncIOMotorDatabase | None) -> str:
    thread_id = str(uuid4())
    doc = _new_doc(thread_id)
    if db is not None:
        await db[CHAT_THREADS_COLLECTION].insert_one(doc)
    else:
        await _mem_put(doc)
    return thread_id


async def get_thread(db: AsyncIOMotorDatabase | None, thread_id: str) -> dict[str, Any] | None:
    if db is not None:
        return await db[CHAT_THREADS_COLLECTION].find_one({"thread_id": thread_id})
    return await _mem_get(thread_id)


async def ensure_thread(db: AsyncIOMotorDatabase | None, thread_id: str) -> dict[str, Any]:
    """Load or create thread (used for WhatsApp stable ids)."""
    doc = await get_thread(db, thread_id)
    if doc is not None:
        return doc
    new_doc = _new_doc(thread_id)
    if db is not None:
        await db[CHAT_THREADS_COLLECTION].insert_one(new_doc)
    else:
        await _mem_put(new_doc)
    return new_doc


async def save_thread(db: AsyncIOMotorDatabase | None, doc: dict[str, Any]) -> None:
    doc["updated_at"] = _now()
    tid = doc["thread_id"]
    if db is not None:
        await db[CHAT_THREADS_COLLECTION].replace_one({"thread_id": tid}, doc, upsert=True)
    else:
        await _mem_put(doc)


async def set_active_plan_id(
    db: AsyncIOMotorDatabase | None, thread_id: str, plan_id: str
) -> None:
    """Link a finalized plan to a chat thread (e.g. WhatsApp wa-* id)."""
    ts = _now()
    if db is not None:
        await db[CHAT_THREADS_COLLECTION].update_one(
            {"thread_id": thread_id},
            {"$set": {"active_plan_id": plan_id, "updated_at": ts}},
        )
        return
    doc = await _mem_get(thread_id)
    if doc is None:
        return
    doc["active_plan_id"] = plan_id
    doc["updated_at"] = ts
    await _mem_put(doc)


def append_message_pair(
    doc: dict[str, Any],
    user_text: str,
    assistant_text: str,
) -> None:
    msgs: list[dict[str, Any]] = doc.setdefault("messages", [])
    ts = _now()
    msgs.append({"role": "user", "content": user_text, "ts": ts})
    msgs.append({"role": "assistant", "content": assistant_text, "ts": _now()})
    if len(msgs) > _MAX_MESSAGES:
        del msgs[: len(msgs) - _MAX_MESSAGES]


def merge_draft(doc: dict[str, Any], fields: DraftPlanFields) -> None:
    doc["draft"] = fields.model_dump()


def draft_from_doc(doc: dict[str, Any]) -> DraftPlanFields:
    return DraftPlanFields.model_validate(doc.get("draft") or {})


def transcript_for_prompt(doc: dict[str, Any]) -> str:
    lines: list[str] = []
    for m in doc.get("messages") or []:
        role = m.get("role", "?")
        content = (m.get("content") or "").strip()
        if content:
            lines.append(f"{role.upper()}: {content}")
    return "\n".join(lines) if lines else "(no prior messages)"
