from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import ConversationSummary, MessageDTO
from app.services.conversations_service import ConversationService

router = APIRouter()

conversation_service = ConversationService()


@router.get("/", response_model=list[ConversationSummary])
def list_conversations(db: Session = Depends(get_db)):
    rows = conversation_service.list_conversations(db)
    return [
        ConversationSummary(id=row["id"], last_updated=row["last_updated"])
        for row in rows
    ]


@router.get("/{conversation_id}/messages", response_model=list[MessageDTO])
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    rows = conversation_service.list_messages_for_conversation(db, conversation_id)
    return [
        MessageDTO(
            id=row["id"],
            direction=row["direction"],
            channel=row["channel"],
            body=row["body"],
            sent_at=row["sent_at"],
        )
        for row in rows
    ]
