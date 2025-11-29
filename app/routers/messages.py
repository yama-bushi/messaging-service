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
from app.services.providers.types import ProviderStatus

from app.models import MessageChannel, MessageType, MessageDirection

router = APIRouter()

conversation_service = ConversationService()


@router.post("/sms", response_model=SendMessageResponse)
def send_sms(
    payload: SmsOrMmsSendRequest,
    db: Session = Depends(get_db),
):
    # Outbound SMS/MMS from customer -> contact
    customer_address = payload.from_
    contact_address = payload.to
    channel = MessageChannel.SMS
    msg_type = MessageType(payload.type)  # "sms" or "mms"

    conversation_id = conversation_service.get_or_create_conversation_id(
        db=db,
        customer_address=customer_address,
        contact_address=contact_address,
    )

    # Send via provider (mocked). ProviderResult.status lets us distinguish
    # success, queued, throttled (429), and error conditions (e.g. 5xx)
    provider = get_provider_for_sms_message(payload.type)
    provider_result = provider.send(payload.dict(by_alias=True))

    # Store message in DB
    msg = conversation_service.create_message(
        db=db,
        conversation_id=conversation_id,
        channel=channel,
        message_type=msg_type,
        direction=MessageDirection.OUTBOUND,
        provider_type="sms",
        provider_message_id=provider_result.provider_message_id,
        from_address=customer_address,
        to_address=contact_address,
        body=payload.body,
        attachments=payload.attachments,
        sent_at=payload.timestamp,
    )

    db.commit()

    # For this take-home, providers are mocked and always return SUCCESS.
    # In a real integration, non-SUCCESS states (TEMPORARY_FAILURE, RATE_LIMITED,
    # PERMANENT_FAILURE) would drive retry/backoff or DLQ behavior.
    if provider_result.status == ProviderStatus.SUCCESS:
        status = "accepted"
    else:
        status = "error"


    return SendMessageResponse(
        message_id=str(msg.id),
        provider_message_id=provider_result.provider_message_id,
        conversation_id=conversation_id,
        status=status,
    )


@router.post("/email", response_model=SendMessageResponse)
def send_email(
    payload: EmailSendRequest,
    db: Session = Depends(get_db),
):
    # Outbound Email from customer -> contact
    customer_address = payload.from_
    contact_address = payload.to
    channel = MessageChannel.EMAIL
    msg_type = MessageType.EMAIL

    conversation_id = conversation_service.get_or_create_conversation_id(
        db=db,
        customer_address=customer_address,
        contact_address=contact_address,
    )

    provider = get_provider_for_email()
    provider_result = provider.send(payload.dict(by_alias=True))

    msg = conversation_service.create_message(
        db=db,
        conversation_id=conversation_id,
        channel=channel,
        message_type=msg_type,
        direction=MessageDirection.OUTBOUND,
        provider_type="email",
        provider_message_id=provider_result.provider_message_id,
        from_address=customer_address,
        to_address=contact_address,
        body=payload.body,
        attachments=payload.attachments,
        sent_at=payload.timestamp,
    )

    db.commit()

    if provider_result.status == ProviderStatus.SUCCESS:
        status = "accepted"
    else:
        status = "error"


    return SendMessageResponse(
        message_id=str(msg.id),
        provider_message_id=provider_result.provider_message_id,
        conversation_id=conversation_id,
        status=status,
    )