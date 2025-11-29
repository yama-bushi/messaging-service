from fastapi import FastAPI

from app.routers import messages, webhooks, conversations

app = FastAPI(title="Messaging Service", version="0.1.0")

app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])

@app.get("/healthz")
def health_check():
    return {"status": "ok"}
