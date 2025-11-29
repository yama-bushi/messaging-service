*** All tests were run in powershell on windows, but scripts should be the same ***
Quick Start (macOS/Linux & Windows)
1. Install dependencies

--macOS/Linux--

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


--Windows PowerShell--

python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

2. Start PostgreSQL
docker-compose up -d

3. Set DATABASE_URL

--macOS/Linux--

export DATABASE_URL="postgresql://messaging_user:messaging_password@127.0.0.1:5432/messaging_service"


--Windows PowerShell--

$env:DATABASE_URL = "postgresql://messaging_user:messaging_password@127.0.0.1:5432/messaging_service"

4. Start the API server

--macOS/Linux--

./bin/start.sh


--Windows PowerShell--

uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

5. Run end-to-end tests

--macOS/Linux--

./bin/test.sh


--Windows PowerShell--

Set-ExecutionPolicy Bypass -Scope Process -Force
.\bin\test.ps1

6. Run pytest suite
pytest -q


If you want to test db creation at startup run these in postgres

drop table contacts cascade;
drop table conversation_participants cascade;
drop table messages cascade;
drop table conversations cascade;

Start the server again and retest (defaults to message_id=1 etc)
--macOS/Linux--
./bin/start.sh

--Windows PowerShell--
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload






Messaging Service — Take Home Implementation

A provider-agnostic messaging microservice implemented in Python/FastAPI with PostgreSQL + SQLAlchemy.

Supports:

Outbound SMS + Email

Inbound SMS + Email webhooks

Long-lived conversation threads

Contact normalization

Provider idempotency

Extensible provider architecture

DB-backed tests (pytest)

Cross-platform run instructions (Linux/macOS/Windows)

This README contains everything required for an evaluator to run the service end-to-end with zero surprises.

1. Features
Messaging API

POST /api/messages/sms

POST /api/messages/email

Webhooks

POST /api/webhooks/sms

POST /api/webhooks/email

Conversations

Long-lived threads keyed by (customer_address, contact_address)

Channel-agnostic grouping (SMS, MMS, Email share the same conversation)

Idempotency

Inbound messages enforce unique (provider_type, provider_message_id) pairing to prevent duplicate inserts on provider retries.

Extensible Provider Model

Providers are registered via:

provider_registry = {
    "sms": SmsProvider(),
    "email": EmailProvider(),
}


New providers (Twilio, SendGrid, WhatsApp, Push) can be added by implementing a simple interface and dropping into the registry.

2. Architecture Overview
 FastAPI Router Layer
 ├── /api/messages/*          → outbound send
 ├── /api/webhooks/*          → inbound callbacks
 └── /api/conversations/*     → retrieval

 Service Layer
 ├── ConversationService       → grouping, idempotency, contact resolution
 ├── ProviderRegistry          → pluggable provider abstraction
 └── MessageService            → persistence

 Data Layer
 ├── SQLAlchemy ORM models     → Contacts, Conversations, Participants, Messages
 └── PostgreSQL (docker)       → relational persistence

Key Design Decisions

Provider abstraction layer (easily extends to new channels)

Channel-agnostic conversation grouping

Webhook idempotency for guaranteed exactly-once inbound handling

Timezone-aware timestamps (datetime.now(UTC))

Hardened SQLAlchemy engine (pool pre-ping, pool recycle)

See Architecture.md for a detailed breakdown.

3. Setup & Installation
Clone and install dependencies
git clone <your-fork-url>
cd messaging-service

python -m venv .venv
source .venv/bin/activate      # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt

4. Start PostgreSQL
docker-compose up -d


This launches a Postgres instance with:

user: messaging_user

password: messaging_password

database: messaging_service

host: 127.0.0.1

5. Environment Variable

Before running the app or tests, set:

macOS / Linux:
export DATABASE_URL="postgresql://messaging_user:messaging_password@127.0.0.1:5432/messaging_service"

Windows PowerShell:
$env:DATABASE_URL = "postgresql://messaging_user:messaging_password@127.0.0.1:5432/messaging_service"

6. Run the Application
Unix (macOS / Linux):
./bin/start.sh

Windows PowerShell:
.\.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload


You should see:

Uvicorn running on http://0.0.0.0:8080

Validate:
curl http://127.0.0.1:8080/healthz
# {"status":"ok"}

7. Run End-to-End API Tests
macOS / Linux:
./bin/test.sh

Windows PowerShell:
Set-ExecutionPolicy Bypass -Scope Process -Force
.\bin\test.ps1


This exercises:

Outbound SMS

Outbound Email

Inbound SMS webhook

Inbound Email webhook

Conversation listing

Message listing

8. Run Pytest Test Suite

Pytest tests use Postgres directly via SQLAlchemy and clean the DB between test runs.

pytest -q


Tests cover:

Conversation reuse

Conversation separation

Webhook idempotency

Timestamp correctness

All timestamps use timezone-aware UTC:

datetime.now(UTC)

9. Extending the System
Add a new provider (Twilio, SendGrid, WhatsApp, Slack DM)

Implement:

class BaseProvider:
    def send(self, payload) -> ProviderResult:
         ...


Add to registry:

provider_registry["twilio"] = TwilioProvider()


Add outbound route (optional).

No changes needed to:

Conversation logic

Models

Webhook processing

This is a key architectural advantage.

10. Production Considerations

In real deployment, you would layer on:

Alembic migrations

API auth

Webhook signature verification

Retry queues (Celery, BackgroundTasks, or SQS)

Structured logging

Background provider delivery

Multi-tenant DB filtering

Horizontal scaling (FastAPI workers, PG pool tuning)

These were not required for the take-home but the system structure cleanly supports them.

11. Summary

This implementation focuses on:

Clean architecture

Clear separation of responsibility

Strong extensibility

Production-minded behaviors (idempotency, UTC timestamps)

A frictionless evaluation experience

All components — API, DB, tests, and helper scripts — are designed for clarity and ease of review.