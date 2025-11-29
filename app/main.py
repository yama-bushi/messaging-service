from fastapi import FastAPI

from app.routers import messages, webhooks, conversations

app = FastAPI(title="Messaging Service", version="0.2.0")

# Match the endpoints expected by bin/test.sh:
# /api/messages/sms, /api/messages/email
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])

# /api/webhooks/sms, /api/webhooks/email
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])

# /api/conversations, /api/conversations/{id}/messages
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])


@app.get("/healthz")
def health_check():
    return {"status": "ok"}
