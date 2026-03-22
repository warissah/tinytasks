import logging

from fastapi import APIRouter, Request

from app.db.sessions import complete_session, insert_session_start
from app.schemas.session import SessionEndBody, SessionStartBody

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/start")
async def session_start(request: Request, body: SessionStartBody) -> dict[str, str]:
    db = getattr(request.app.state, "mongo_db", None)
    if db is not None:
        try:
            await insert_session_start(db, body.task_id, body.started_at)
        except Exception:
            logger.exception("Failed to persist session start to Mongo")
    return {"status": "ok", "task_id": body.task_id}


@router.post("/end")
async def session_end(request: Request, body: SessionEndBody) -> dict[str, str]:
    db = getattr(request.app.state, "mongo_db", None)
    if db is not None:
        try:
            n = await complete_session(db, body.task_id, body.ended_at, body.reflection)
            if n == 0:
                logger.warning(
                    "session end: no open session for task_id=%s", body.task_id
                )
        except Exception:
            logger.exception("Failed to persist session end to Mongo")
    return {"status": "ok", "reflection": body.reflection}
