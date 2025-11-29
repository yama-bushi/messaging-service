Messaging Service — Take-Home Implementation

A provider-agnostic messaging microservice implemented in Python / FastAPI with PostgreSQL + SQLAlchemy.
This README provides concise, cross-platform instructions and an overview of the system architecture.

Quick Start Instructions (macOS/Linux & Windows)

All steps required to run the service end-to-end.

1. Install Dependencies

macOS / Linux

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


Windows PowerShell

python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

2. Start PostgreSQL

All Platforms

docker-compose up -d

3. Set DATABASE_URL

macOS / Linux

export DATABASE_URL="postgresql://messaging_user:messaging_password@127.0.0.1:5432/messaging_service"


Windows PowerShell

$env:DATABASE_URL = "postgresql://messaging_user:messaging_password@127.0.0.1:5432/messaging_service"

4. Start the API Server

macOS / Linux

./bin/start.sh


Windows PowerShell

uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload


Health check:

curl http://127.0.0.1:8080/healthz

5. Run End-to-End Tests

macOS / Linux

./bin/test.sh


Windows PowerShell

Set-ExecutionPolicy Bypass -Scope Process -Force
.\bin\test.ps1

6. Run Pytest

All Platforms

pytest -q

7. Optional: Reset the Database (for cold-start testing)

In psql or any SQL client:

drop table contacts cascade;
drop table conversation_participants cascade;
drop table messages cascade;
drop table conversations cascade;


Restart the server and re-run tests.

Features
Messaging API

POST /api/messages/sms

POST /api/messages/email

Webhooks

POST /api/webhooks/sms

POST /api/webhooks/email

Conversations

Long-lived, automatically reused

Cross-channel: SMS, MMS, and Email all participate in the same thread

Keyed by (customer_address, contact_address)

Idempotency

Inbound webhook deduplication on:

(provider_type, provider_message_id)


Prevents duplicate inserts on provider retries.

Extensible Provider Abstraction

Providers are pluggable through a registry:

provider_registry = {
    "sms": SmsProvider(),
    "email": EmailProvider(),
}


Adding Twilio, SendGrid, or WhatsApp requires only implementing the provider interface.

Architecture Overview
FastAPI Router Layer
 ├── /api/messages/*          → outbound send
 ├── /api/webhooks/*          → inbound callbacks
 └── /api/conversations/*     → retrieval

Service Layer
 ├── ConversationService       → grouping, idempotency, contact resolution
 ├── ProviderRegistry          → pluggable providers
 └── MessageService            → persistence

Data Layer
 ├── SQLAlchemy ORM            → Contacts, Conversations, Participants, Messages
 └── PostgreSQL (docker)       → relational persistence

Key Architectural Choices

Provider abstraction to support multiple messaging backends

Channel-agnostic conversation grouping

Webhook idempotency ensures exactly-once inbound message handling

UTC-aware timestamps

Hardened SQLAlchemy engine (pre-ping, connection recycling)

See Architecture.md for more detail.

Setup (Full)
git clone <your-fork-url>
cd messaging-service
python -m venv .venv
source .venv/bin/activate         # or .\.venv\Scripts\activate on Windows
pip install -r requirements.txt
docker-compose up -d
export DATABASE_URL=...

Extending the System
Adding a New Provider

Implement the provider interface:

class BaseProvider:
    def send(self, payload) -> ProviderResult:
         ...


Register it:

provider_registry["twilio"] = TwilioProvider()


No changes required in:

Conversations

Models

Webhooks

Message grouping logic

Production-Ready Considerations

Supported but not required for the take-home:

Alembic migrations

API authentication

Webhook signature validation

Retry/backoff queues

Structured logging

Deployment with multiple workers

Multi-tenant filtering

Summary

This implementation emphasizes:

Clear, modular architecture

Clean provider extensibility

Robust idempotency

UTC-based timestamps

Simple setup across macOS, Linux, and Windows

Zero-surprise evaluation experience

All necessary instructions, scripts, and tests are included for a complete review.