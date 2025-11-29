from datetime import datetime, UTC
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# Enums -------------------------------------------------------------------------


class ContactAddressType(str, PyEnum):
    PHONE = "phone"
    EMAIL = "email"


class MessageChannel(str, PyEnum):
    SMS = "sms"
    EMAIL = "email"


class MessageType(str, PyEnum):
    SMS = "sms"
    MMS = "mms"
    EMAIL = "email"


class MessageDirection(str, PyEnum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class ParticipantRole(str, PyEnum):
    CUSTOMER = "customer"
    CONTACT = "contact"


# Models ------------------------------------------------------------------------


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    address_type = Column(Enum(ContactAddressType), nullable=False)
    is_customer_owned = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # relationships
    customer_conversations = relationship(
        "ConversationParticipant",
        back_populates="contact",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # A given address/type combination is unique
        Index(
            "uq_contacts_address_type",
            "address",
            "address_type",
            unique=True,
        ),
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC)
)
    updated_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    participants = relationship(
        "ConversationParticipant",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    contact_id = Column(
        Integer,
        ForeignKey("contacts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role = Column(Enum(ParticipantRole), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))

    conversation = relationship("Conversation", back_populates="participants")
    contact = relationship("Contact", back_populates="customer_conversations")

    __table_args__ = (
        # Index to quickly find conversations by contact
        Index("idx_conv_participants_contact_id", "contact_id"),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )

    channel = Column(Enum(MessageChannel), nullable=False)
    message_type = Column(Enum(MessageType), nullable=False)
    direction = Column(Enum(MessageDirection), nullable=False)

    provider_type = Column(String, nullable=True)
    provider_message_id = Column(String, nullable=True)

    from_contact_id = Column(
        Integer, ForeignKey("contacts.id"), nullable=False, index=True
    )
    to_contact_id = Column(
        Integer, ForeignKey("contacts.id"), nullable=False, index=True
    )

    body = Column(Text, nullable=True)
    attachments = Column(JSON, nullable=True)

    sent_at = Column(DateTime, nullable=False)
    received_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    conversation = relationship("Conversation", back_populates="messages")
    # From/To relationships are optional to navigate from Contact → Messages if needed
    from_contact = relationship("Contact", foreign_keys=[from_contact_id])
    to_contact = relationship("Contact", foreign_keys=[to_contact_id])

    __table_args__ = (
        # Fast query for "show me the thread"
        Index("idx_messages_conversation_sent_at", "conversation_id", "sent_at"),
        # Idempotency for provider callbacks (webhooks)
        Index(
            "uq_messages_provider_type_message_id",
            "provider_type",
            "provider_message_id",
            unique=True,
            postgresql_where=(
                provider_message_id.isnot(None)  # type: ignore[attr-defined]
            ),
        ),
    )
