# Messaging Service — Take-Home Implementation

A provider-agnostic messaging microservice implemented in **Python / FastAPI** with **PostgreSQL + SQLAlchemy**.  
This README provides compact cross-platform instructions and a clear architecture overview for evaluators.

---

# Quick Start Instructions

All steps required to run the service end-to-end on macOS/Linux or Windows.

---

## 1. Install Dependencies

| macOS / Linux | Windows PowerShell |
|---------------|-------------------|
| ```bash       | ```powershell     |
| python -m venv .venv | python -m venv .venv |
| source .venv/bin/activate | .\.venv\Scripts\activate |
| pip install -r requirements.txt | pip install -r requirements.txt |
| ``` | ``` |

---

## 2. Start PostgreSQL

```bash
docker-compose up -d
```

---

## 3. Set `DATABASE_URL`

| macOS / Linux | Windows PowerShell |
|---------------|-------------------|
| ```bash       | ```powershell     |
| export DATABASE_URL="postgresql://messaging_user:messaging_password@127.0.0.1:5432/messaging_service" | $env:DATABASE_URL = "postgresql://messaging_user:messaging_password@127.0.0.1:5432/messaging_service" |
| ``` | ``` |

---

## 4. Start the API Server

| macOS / Linux | Windows PowerShell |
|---------------|-------------------|
| ```bash       | ```powershell     |
| ./bin/start.sh | uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload |
| ``` | ``` |

Health check:
```bash
curl http://127.0.0.1:8080/healthz
```

---

## 5. Run End-to-End Tests

| macOS / Linux | Windows PowerShell |
|---------------|-------------------|
| ```bash       | ```powershell     |
| ./bin/test.sh | Set-ExecutionPolicy Bypass -Scope Process -Force |
|               | .\bin\test.ps1 |
| ``` | ``` |

---

## 6. Run Pytest Suite

```bash
pytest -q
```

---

## 7. Optional: Reset Database Tables

If you want to validate cold-start behavior:

```sql
drop table contacts cascade;
drop table conversation_participants cascade;
drop table messages cascade;
drop table conversations cascade;
```

Restart server using the commands in step 4.

---

# Features

### Messaging API
- `POST /api/messages/sms`
- `POST /api/messages/email`

### Webhooks
- `POST /api/webhooks/sms`
- `POST /api/webhooks/email`

### Conversations
- Long-lived, persistent threads  
- Shared across SMS, MMS, Email  
- Keyed by `(customer_address, contact_address)`

### Idempotency
Inbound messages deduplicated on:

```
(provider_type, provider_message_id)
```

### Provider Abstraction
Providers are injected via a registry:

```python
provider_registry = {
    "sms": SmsProvider(),
    "email": EmailProvider(),
}
```

To add Twilio, SendGrid, WhatsApp, or others, implement the provider interface and register it.

---

# Architecture Overview

```
FastAPI Router Layer
 ├── /api/messages/*          → outbound sends
 ├── /api/webhooks/*          → inbound callbacks
 └── /api/conversations/*     → retrieval APIs

Service Layer
 ├── ConversationService       → grouping, contact resolution, idempotency
 ├── ProviderRegistry          → pluggable provider abstraction
 └── MessageService            → ORM persistence

Data Layer
 ├── SQLAlchemy ORM Models     → Contacts, Conversations, Participants, Messages
 └── PostgreSQL (docker)       → relational persistence
```

### Key Design Choices
- Provider interface abstracts 3rd-party vendors  
- Channel-agnostic conversation grouping  
- Webhook idempotency guarantees exactly-once inserts  
- UTC timestamps (`datetime.now(UTC)`)  
- Hardened SQLAlchemy engine (pre-ping, pool recycle)

---

# Setup (Full Version)

```bash
git clone <your-fork-url>
cd messaging-service
python -m venv .venv
source .venv/bin/activate      # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
docker-compose up -d
export DATABASE_URL=...
```

---

# Extending the System

### Add a New Provider

1. Implement:

```python
class BaseProvider:
    def send(self, payload) -> ProviderResult:
        ...
```

2. Register:

```python
provider_registry["twilio"] = TwilioProvider()
```

No changes required to:

- Conversations  
- Models  
- Webhook processing  
- Message grouping logic  

---

# Production Considerations

Supported but out of scope for the take-home:

- Alembic migrations  
- API authentication  
- Webhook signature verification  
- Delivery retry/backoff queues  
- Structured logging  
- Multi-tenant filtering  
- Horizontal worker scaling  

---

# Summary

This implementation prioritizes:

- Clear architectural separation  
- Provider extensibility  
- Robust idempotency  
- UTC timestamps  
- Cross-platform execution  
- Straightforward evaluation experience  

All scripts and tests needed for a complete review are included.
