from typing import Dict

from app.services.providers.base import BaseProvider
from app.services.providers.sms_provider import SmsProvider
from app.services.providers.email_provider import EmailProvider


# Simple provider registry keyed by "channel"
# In the future you could support multiple providers per channel.
provider_registry: Dict[str, BaseProvider] = {
    "sms": SmsProvider(),
    "email": EmailProvider(),
}


def get_provider_for_sms_message(message_type: str) -> BaseProvider:
    # For now "sms" and "mms" both go through the same SMS provider
    return provider_registry["sms"]


def get_provider_for_email() -> BaseProvider:
    return provider_registry["email"]
