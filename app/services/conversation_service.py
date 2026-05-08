from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.conversation import Conversation, Message


def create_conversation(db: Session, title: str = "New Conversation") -> Conversation:
    conv = Conversation(title=title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def list_conversations(db: Session, offset: int = 0, limit: int = 20) -> list[Conversation]:
    return (
        db.query(Conversation)
        .order_by(Conversation.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_conversation(db: Session, conversation_id: int) -> Optional[Conversation]:
    return (
        db.query(Conversation)
        .options(joinedload(Conversation.messages))
        .filter(Conversation.id == conversation_id)
        .first()
    )


def delete_conversation(db: Session, conversation_id: int) -> bool:
    conv = db.get(Conversation, conversation_id)
    if not conv:
        return False
    db.delete(conv)
    db.commit()
    return True


def add_message(db: Session, conversation_id: int, role: str, content: str) -> Message:
    msg = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
