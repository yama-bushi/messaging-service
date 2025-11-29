1. System Overview

The messaging-service implements a unified API layer for sending and receiving messages across multiple channels (SMS, MMS, Email).
Core responsibilities:

Normalize different provider payloads into consistent internal models

Group messages into long-lived conversations

Persist messages with strict inbound idempotency

Provide a provider-agnostic interface for future channels (WhatsApp, Push, Voice)

The system is intentionally modular: transport, provider logic, routing, conversation grouping, and persistence are isolated.

2. High-Level Architecture
 FastAPI Layer
 ├── /api/messages/*       → outbound send (sms, email)
 ├── /api/webhooks/*       → inbound provider callbacks
 └── /api/conversations/*  → query conversations + messages

 Service Layer
 ├── ProviderRegistry       → provider abstraction (SMS / Email / future)
 ├── ConversationService    → contact resolution, thread grouping, idempotency
 └── Message Insertion      → DB persistence and FK resolution

 Data Layer
 ├── SQLAlchemy models      → Conversation, Contacts, Participants, Messages
 └── PostgreSQL             → relational core


The architecture isolates routing, domain logic, and provider integration cleanly so each evolves independently.

3. Data Model Summary
 - contacts -

Unique identity representing either a customer-owned address or external contact

Normalized by (address, type) to avoid duplicates

 - conversations -

Long-lived threads keyed by (customer_address, contact_address)

Independent of channel/provider

 - conversation_participants -

Role-based membership (CUSTOMER, CONTACT)

Allows future multi-party conversations

messages

Channel-agnostic storage

Supports provider metadata (provider type, provider_message_id)

Enforces idempotency via (provider_type, provider_message_id) unique identity for inbound webhook replays

4. Key Design Decisions
4.1 Provider Abstraction Layer (Extensible Provider Registry)

Providers are registered in a simple dictionary:

provider_registry = {
    "sms": SmsProvider(),
    "email": EmailProvider(),
}


Each provider implements:

class BaseProvider(Protocol):
    def send(self, payload) -> ProviderResult:
        ...


This enables:

Swapping providers without modifying business logic

Adding new providers (e.g., Twilio, SendGrid) via drop-in classes

Multi-provider routing (load-balanced, failover policies)

Channel expansion (WhatsApp, Push, Slack DM)

This separation ensures messaging logic never needs to change when adding new transports.

4.2 Conversation Normalization and Grouping

The system treats conversations as channel-agnostic, so SMS, MMS, and Email all belong to the same thread if sender/recipient pairs match:

(customer_address, contact_address) → conversation_id


This is a high-impact design choice because:

It unifies all messaging types under a single thread

Avoids fragmented threads when channels change

Makes querying dramatically simpler

Extends naturally to multi-channel customer support

The use of aliased() in SQLAlchemy ensures correct multi-join resolution for participant queries.

4.3 Inbound Webhook Idempotency (Guaranteed Exactly-Once Processing)

Inbound messages may be retried by providers, so each inbound callback includes a unique identifier:

SMS/MMS: messaging_provider_id

Email: xillio_id

A partial unique index over (provider_type, provider_message_id) ensures:

Duplicate retries never insert multiple inbound messages

Retry handlers remain safe

System is resilient to provider flakiness

This is critical for correctness and matches real-world messaging infrastructure patterns.

5. PostgreSQL & SQLAlchemy Layer

Connection pool hardened with:

pool_pre_ping=True (drops stale connections)

pool_recycle=1800 (prevents long-lived TCP issues)

Declarative models with explicit indexes for:

fast conversation lookup

idempotency enforcement

chronological message retrieval

init_db() auto-creates schema for the take-home; in production this would be driven by Alembic migrations.

6. Extensibility Points
Additional Providers

Add new classes implementing BaseProvider.
Register them in provider_registry.
Routing logic automatically adapts.

Additional Channels

Extend the MessageChannel enum and add routing paths in the FastAPI layer.
All core services reuse the same conversation + message model.

Provider Failover

Provider registry can be expanded to:

provider_registry["sms"] = [PrimaryProvider(), BackupProvider()]


and wrapped in a retry policy.

Background Tasks

Outbound sends can be queued using BackgroundTasks for async behavior.

Tenant Support

Add tenant_id to Contact, Conversation, and filter queries globally.