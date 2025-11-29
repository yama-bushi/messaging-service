from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import (
    SmsOrMmsWebhookPayload,
    EmailWebhookPayload,
    WebhookResponse,
)
from app.services.conversations_service import ConversationService

router = APIRouter()

conversation_service = ConversationService()


@router.post("/sms", response_model=WebhookResponse)
def sms_webhook(
    payload: SmsOrMmsWebhookPayload,
    db: Session = Depends(get_db),
):
    # In Commit 3, we'll:
    # - ensure idempotency using provider_message_id
    # - resolve conversation and insert inbound message
    channel = "sms"

    conversation_service.get_or_create_conversation_id(
        db=db,
        from_address=payload.from_,
        to_address=payload.to,
        channel=channel,
    )

    return WebhookResponse(status="ok")


@router.post("/email", response_model=WebhookResponse)
def email_webhook(
    payload: EmailWebhookPayload,
    db: Session = Depends(get_db),
):
    channel = "email"

    conversation_service.get_or_create_conversation_id(
        db=db,
        from_address=payload.from_,
        to_address=payload.to,
        channel=channel,
    )

    return WebhookResponse(status="ok")
