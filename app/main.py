from fastapi import FastAPI

from app.db import init_db
from app.routers import messages, webhooks, conversations

# Ensure DB tables are created
init_db()

app = FastAPI(title="Messaging Service", version="0.3.0")

# Match the endpoints expected by bin/test.sh:
"""
    POST /api/messages/sms
    POST /api/messages/email
    POST /api/webhooks/sms
    POST /api/webhooks/email
    GET  /api/conversations
    GET  /api/conversations/{id}/messages
"""
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])


@app.get("/healthz")
def health_check():
    return {"status": "ok"}
