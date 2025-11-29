from datetime import datetime,UTC

from app.services.conversations_service import ConversationService
from app.models import (
    MessageChannel,
    MessageType,
    MessageDirection,
)


def test_conversation_reused_for_same_customer_contact_pair(db_session):
    """
    Given the same (customer_address, contact_address) pair,
    ConversationService should return the same conversation_id.
    """
    svc = ConversationService()

    customer = "+15551234567"
    contact = "+15557654321"

    conv_id_1 = svc.get_or_create_conversation_id(
        db=db_session,
        customer_address=customer,
        contact_address=contact,
    )
    conv_id_2 = svc.get_or_create_conversation_id(
        db=db_session,
        customer_address=customer,
        contact_address=contact,
    )

    assert conv_id_1 == conv_id_2


def test_conversation_differs_for_different_contact(db_session):
    """
    Different contacts should result in different conversations, even for the same customer.
    """
    svc = ConversationService()

    customer = "+15551234567"
    contact_a = "+15557654321"
    contact_b = "+15559876543"

    conv_id_a = svc.get_or_create_conversation_id(
        db=db_session,
        customer_address=customer,
        contact_address=contact_a,
    )
    conv_id_b = svc.get_or_create_conversation_id(
        db=db_session,
        customer_address=customer,
        contact_address=contact_b,
    )

    assert conv_id_a != conv_id_b


def test_inbound_idempotency_on_provider_message_id(db_session):
    """
    Inbound messages with the same (provider_type, provider_message_id)
    should be treated as idempotent: the first insert creates a row,
    subsequent checks report 'exists' and do not require another insert.
    """
    svc = ConversationService()

    customer = "+15551234567"
    contact = "+15557654321"
    provider_type = "sms"
    provider_message_id = "provider-12345"

    # Create conversation and initial inbound message
    conversation_id = svc.get_or_create_conversation_id(
        db=db_session,
        customer_address=customer,
        contact_address=contact,
    )

    svc.create_message(
        db=db_session,
        conversation_id=conversation_id,
        channel=MessageChannel.SMS,
        message_type=MessageType.SMS,
        direction=MessageDirection.INBOUND,
        provider_type=provider_type,
        provider_message_id=provider_message_id,
        from_address=contact,
        to_address=customer,
        body="First inbound",
        attachments=None,

        sent_at = datetime.now(UTC)

    )
    db_session.commit()

    # First check: message should exist
    assert svc.inbound_message_exists(
        db=db_session,
        provider_type=provider_type,
        provider_message_id=provider_message_id,
    )

    # Different provider_message_id should not be considered existing
    assert not svc.inbound_message_exists(
        db=db_session,
        provider_type=provider_type,
        provider_message_id="provider-OTHER",
    )
