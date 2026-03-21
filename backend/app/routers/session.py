from fastapi import APIRouter

from app.schemas.session import SessionEndBody, SessionStartBody

router = APIRouter()


@router.post("/start")
def session_start(body: SessionStartBody) -> dict[str, str]:
    """Stub: persist session in Mongo when ready."""
    return {"status": "ok", "task_id": body.task_id}


@router.post("/end")
def session_end(body: SessionEndBody) -> dict[str, str]:
    """Stub: persist session end in Mongo when ready."""
    return {"status": "ok", "reflection": body.reflection}
