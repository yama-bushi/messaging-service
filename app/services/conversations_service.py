from datetime import datetime,UTC
from typing import Optional

from sqlalchemy.orm import Session, aliased
from sqlalchemy import and_


from app.models import (
    Contact,
    Conversation,
    ConversationParticipant,
    Message,
    ContactAddressType,
    ParticipantRole,
    MessageChannel,
    MessageType,
    MessageDirection,
)


class ConversationService:
    """
    Handles conversation lookup/creation and message retrieval.
    """

    # -------------------------------------------------------------------------
    # Contact helpers
    # -------------------------------------------------------------------------

    def _infer_address_type(self, address: str) -> ContactAddressType:
        if "@" in address:
            return ContactAddressType.EMAIL
        return ContactAddressType.PHONE

    def _get_or_create_contact(
        self,
        db: Session,
        address: str,
        is_customer_owned: bool,
    ) -> Contact:
        address_type = self._infer_address_type(address)

        contact = (
            db.query(Contact)
            .filter(
                Contact.address == address,
                Contact.address_type == address_type,
            )
            .first()
        )
        if contact:
            # Optionally update is_customer_owned if needed
            if is_customer_owned and not contact.is_customer_owned:
                contact.is_customer_owned = True
            return contact

        contact = Contact(
            address=address,
            address_type=address_type,
            is_customer_owned=is_customer_owned,
        )
        db.add(contact)
        db.flush()  # assign id
        return contact

    # -------------------------------------------------------------------------
    # Conversation helpers
    # -------------------------------------------------------------------------
    def get_or_create_conversation_id(
        self,
        db: Session,
        customer_address: str,
        contact_address: str,
    ) -> int:
        """
        Long-lived conversation keyed by (customer_identity, contact_identity),
        regardless of channel/provider.
        """

        customer = self._get_or_create_contact(
            db=db,
            address=customer_address,
            is_customer_owned=True,
        )
        contact = self._get_or_create_contact(
            db=db,
            address=contact_address,
            is_customer_owned=False,
        )

        # Create two aliases for conversation_participants:
        cp_customer = aliased(ConversationParticipant)
        cp_contact = aliased(ConversationParticipant)

        # Try to find an existing conversation with these exact participants
        conv = (
            db.query(Conversation)
            .join(
                cp_customer,
                and_(
                    cp_customer.conversation_id == Conversation.id,
                    cp_customer.contact_id == customer.id,
                    cp_customer.role == ParticipantRole.CUSTOMER,
                ),
            )
            .join(
                cp_contact,
                and_(
                    cp_contact.conversation_id == Conversation.id,
                    cp_contact.contact_id == contact.id,
                    cp_contact.role == ParticipantRole.CONTACT,
                ),
            )
            .first()
        )

        if conv:
            return conv.id

        # Create a new conversation
        conv = Conversation()
        db.add(conv)
        db.flush()  # assign id

        db.add_all(
            [
                ConversationParticipant(
                    conversation_id=conv.id,
                    contact_id=customer.id,
                    role=ParticipantRole.CUSTOMER,
                ),
                ConversationParticipant(
                    conversation_id=conv.id,
                    contact_id=contact.id,
                    role=ParticipantRole.CONTACT,
                ),
            ]
        )
        db.flush()
        return conv.id


    # -------------------------------------------------------------------------
    # Message helpers
    # -------------------------------------------------------------------------

    def create_message(
        self,
        db: Session,
        *,
        conversation_id: int,
        channel: MessageChannel,
        message_type: MessageType,
        direction: MessageDirection,
        provider_type: Optional[str],
        provider_message_id: Optional[str],
        from_address: str,
        to_address: str,
        body: str,
        attachments: Optional[list[str]],
        sent_at: datetime,
    ) -> Message:
        """
        Insert a message row and bump conversation.updated_at.
        """

        # Resolve contacts again to attach proper FKs
        from_contact = self._get_or_create_contact(
            db=db,
            address=from_address,
            is_customer_owned=direction == MessageDirection.OUTBOUND,
        )
        to_contact = self._get_or_create_contact(
            db=db,
            address=to_address,
            is_customer_owned=direction == MessageDirection.INBOUND,
        )

        msg = Message(
            conversation_id=conversation_id,
            channel=channel,
            message_type=message_type,
            direction=direction,
            provider_type=provider_type,
            provider_message_id=provider_message_id,
            from_contact_id=from_contact.id,
            to_contact_id=to_contact.id,
            body=body,
            attachments=attachments,
            sent_at=sent_at,
            received_at=datetime.now(UTC)
        )
        db.add(msg)

        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv:
            conv.updated_at = datetime.now(UTC)

        db.flush()
        return msg

    # -------------------------------------------------------------------------
    # Query helpers for API
    # -------------------------------------------------------------------------

    def list_conversations(self, db: Session) -> list[dict]:
        conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
        return [
            {
                "id": c.id,
                "last_updated": c.updated_at or c.created_at,
            }
            for c in conversations
        ]

    def list_messages_for_conversation(self, db: Session, conversation_id: int) -> list[dict]:
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.sent_at.asc())
            .all()
        )
        return [
            {
                "id": m.id,
                "direction": m.direction.value,
                "channel": m.channel.value,
                "body": m.body or "",
                "sent_at": m.sent_at,
            }
            for m in messages
        ]

    # -------------------------------------------------------------------------
    # Idempotency for inbound webhooks
    # -------------------------------------------------------------------------

    def inbound_message_exists(
        self,
        db: Session,
        provider_type: str,
        provider_message_id: str,
    ) -> bool:
        if not provider_message_id:
            return False

        existing = (
            db.query(Message)
            .filter(
                Message.provider_type == provider_type,
                Message.provider_message_id == provider_message_id,
            )
            .first()
        )
        return existing is not None
