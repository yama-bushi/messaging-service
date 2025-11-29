import uuid
from .base import BaseProvider
from .types import ProviderResult, ProviderStatus

class SmsProvider(BaseProvider):
    def send(self, payload: dict) -> ProviderResult:
        """
        Mock provider implementation.
        Always returns success, but structure supports future 500/429 logic.
        """
        return ProviderResult(
            status=ProviderStatus.SUCCESS,
            provider_message_id=f"sms-{uuid.uuid4()}"
        )
