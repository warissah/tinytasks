from fastapi import APIRouter, Request

from app.schemas.chat import ChatFinalizeBody, ChatMessageBody, ChatMessageResponse
from app.schemas.plan import PlanResponse
from app.services.chat_pipeline import run_chat_turn, run_finalize

router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(request: Request, body: ChatMessageBody) -> ChatMessageResponse:
    db = getattr(request.app.state, "mongo_db", None)
    return await run_chat_turn(db, thread_id=body.thread_id, text=body.text)


@router.post("/finalize", response_model=PlanResponse)
async def chat_finalize(request: Request, body: ChatFinalizeBody) -> PlanResponse:
    db = getattr(request.app.state, "mongo_db", None)
    return await run_finalize(db, body.thread_id)
