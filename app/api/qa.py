from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.qa_service import ask_sync, ask_stream

router = APIRouter(prefix="/qa", tags=["知识问答"])


class QARequest(BaseModel):
    query: str
    conversation_id: int | None = None


@router.post("")
async def api_ask(body: QARequest, db: Session = Depends(get_db)):
    """单轮知识问答，返回答案与引用来源。"""
    result = ask_sync(body.query, db)
    return result


@router.post("/stream")
async def api_ask_stream(body: QARequest):
    """流式知识问答，SSE 实时输出。"""
    return StreamingResponse(
        ask_stream(body.query),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
