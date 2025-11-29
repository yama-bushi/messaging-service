from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import (
    SmsOrMmsWebhookPayload,
    EmailWebhookPayload,
    WebhookResponse,
)
from app.services.conversations_service import ConversationService
from app.models import MessageChannel, MessageType, MessageDirection

router = APIRouter()

conversation_service = ConversationService()


@router.post("/sms", response_model=WebhookResponse)
def sms_webhook(
    payload: SmsOrMmsWebhookPayload,
    db: Session = Depends(get_db),
):
    # Inbound SMS/MMS from contact -> customer
    provider_type = "sms"
    provider_message_id = payload.messaging_provider_id

    # Idempotency check
    if conversation_service.inbound_message_exists(
        db=db,
        provider_type=provider_type,
        provider_message_id=provider_message_id,
    ):
        return WebhookResponse(status="ok")

    # For inbound webhooks, `from` is contact, `to` is customer
    customer_address = payload.to
    contact_address = payload.from_
    channel = MessageChannel.SMS
    msg_type = MessageType(payload.type)

    conversation_id = conversation_service.get_or_create_conversation_id(
        db=db,
        customer_address=customer_address,
        contact_address=contact_address,
    )

    conversation_service.create_message(
        db=db,
        conversation_id=conversation_id,
        channel=channel,
        message_type=msg_type,
        direction=MessageDirection.INBOUND,
        provider_type=provider_type,
        provider_message_id=provider_message_id,
        from_address=contact_address,
        to_address=customer_address,
        body=payload.body,
        attachments=payload.attachments,
        sent_at=payload.timestamp,
    )

    db.commit()

    return WebhookResponse(status="ok")


@router.post("/email", response_model=WebhookResponse)
def email_webhook(
    payload: EmailWebhookPayload,
    db: Session = Depends(get_db),
):
    provider_type = "email"
    provider_message_id = payload.xillio_id

    if conversation_service.inbound_message_exists(
        db=db,
        provider_type=provider_type,
        provider_message_id=provider_message_id,
    ):
        return WebhookResponse(status="ok")

    # Inbound email: from contact -> to customer
    customer_address = payload.to
    contact_address = payload.from_
    channel = MessageChannel.EMAIL
    msg_type = MessageType.EMAIL

    conversation_id = conversation_service.get_or_create_conversation_id(
        db=db,
        customer_address=customer_address,
        contact_address=contact_address,
    )

    conversation_service.create_message(
        db=db,
        conversation_id=conversation_id,
        channel=channel,
        message_type=msg_type,
        direction=MessageDirection.INBOUND,
        provider_type=provider_type,
        provider_message_id=provider_message_id,
        from_address=contact_address,
        to_address=customer_address,
        body=payload.body,
        attachments=payload.attachments,
        sent_at=payload.timestamp,
    )

    db.commit()

    return WebhookResponse(status="ok")
