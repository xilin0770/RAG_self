from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.conversation_service import (
    create_conversation,
    list_conversations,
    get_conversation,
    delete_conversation,
)

router = APIRouter(prefix="/conversations", tags=["对话管理"])


class ConversationCreate(BaseModel):
    title: str = "New Conversation"


@router.post("")
async def api_create_conversation(body: ConversationCreate, db: Session = Depends(get_db)):
    """创建新对话。"""
    conv = create_conversation(db, title=body.title)
    return {"id": conv.id, "title": conv.title}


@router.get("")
async def api_list_conversations(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取对话列表。"""
    convs = list_conversations(db, offset=offset, limit=limit)
    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in convs
    ]


@router.get("/{conversation_id}")
async def api_get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """获取对话详情，包含历史消息。"""
    conv = get_conversation(db, conversation_id)
    if not conv:
        return {"error": "Conversation not found"}
    return {
        "id": conv.id,
        "title": conv.title,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "citations": m.citations or [],
            }
            for m in conv.messages
        ],
    }


@router.delete("/{conversation_id}")
async def api_delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """删除对话及其所有消息。"""
    success = delete_conversation(db, conversation_id)
    return {"deleted": success}
