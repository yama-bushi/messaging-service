from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field



# Outbound send schemas

class SmsOrMmsSendRequest(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    type: str  # "sms" or "mms"
    body: str
    attachments: Optional[List[str]] = None
    timestamp: datetime


class EmailSendRequest(BaseModel):
    from_: EmailStr = Field(..., alias="from")
    to: EmailStr
    body: str
    attachments: Optional[List[str]] = None
    timestamp: datetime


class SendMessageResponse(BaseModel):
    message_id: str
    provider_message_id: Optional[str] = None
    conversation_id: Optional[int] = None
    status: str = "accepted"


# Inbound webhook schemas

class SmsOrMmsWebhookPayload(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    type: str  # "sms" or "mms"
    messaging_provider_id: str
    body: str
    attachments: Optional[List[str]] = None
    timestamp: datetime


class EmailWebhookPayload(BaseModel):
    from_: EmailStr = Field(..., alias="from")
    to: EmailStr
    xillio_id: str
    body: str
    attachments: Optional[List[str]] = None
    timestamp: datetime


class WebhookResponse(BaseModel):
    status: str = "ok"


# Conversation DTOs

class ConversationSummary(BaseModel):
    id: int
    last_updated: datetime


class MessageDTO(BaseModel):
    id: int
    direction: str
    channel: str
    body: str
    sent_at: datetime
