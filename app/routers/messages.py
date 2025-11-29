from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import (
    SmsOrMmsSendRequest,
    EmailSendRequest,
    SendMessageResponse,
)
from app.services.conversations_service import ConversationService
from app.services.providers import (
    get_provider_for_sms_message,
    get_provider_for_email,
)

router = APIRouter()

conversation_service = ConversationService()


@router.post("/sms", response_model=SendMessageResponse)
def send_sms(
    payload: SmsOrMmsSendRequest,
    db: Session = Depends(get_db),
):
    # Determine channel
    channel = "sms"

    # Lookup/create conversation
    conversation_id = conversation_service.get_or_create_conversation_id(
        db=db,
        from_address=payload.from_,
        to_address=payload.to,
        channel=channel,
    )

    # Send via provider (stubbed for now)
    provider = get_provider_for_sms_message(payload.type)
    provider_result = provider.send(payload.dict(by_alias=True))

    # Return a structured response
    return SendMessageResponse(
        message_id="local-sms-message-id",
        provider_message_id=provider_result.provider_message_id,
        conversation_id=conversation_id,
        status="accepted" if provider_result.success else "failed",
    )


@router.post("/email", response_model=SendMessageResponse)
def send_email(
    payload: EmailSendRequest,
    db: Session = Depends(get_db),
):
    channel = "email"

    conversation_id = conversation_service.get_or_create_conversation_id(
        db=db,
        from_address=payload.from_,
        to_address=payload.to,
        channel=channel,
    )

    provider = get_provider_for_email()
    provider_result = provider.send(payload.dict(by_alias=True))

    return SendMessageResponse(
        message_id="local-email-message-id",
        provider_message_id=provider_result.provider_message_id,
        conversation_id=conversation_id,
        status="accepted" if provider_result.success else "failed",
    )
