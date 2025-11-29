from typing import Dict, Any

from app.services.providers.base import BaseProvider, ProviderResult


class SmsProvider(BaseProvider):
    """
    Mock SMS/MMS provider implementation.
    In Commit 3/4 we can simulate 429/500 errors and retries.
    """

    def send(self, payload: Dict[str, Any]) -> ProviderResult:
        # For now, always succeed with a mock provider message id.
        # We preserve shape so we can easily add error simulation later.
        return ProviderResult(success=True, provider_message_id="mock-sms-id")
