from typing import Dict, Any

from app.services.providers.base import BaseProvider, ProviderResult


class EmailProvider(BaseProvider):
    """
    Mock Email provider implementation.
    """

    def send(self, payload: Dict[str, Any]) -> ProviderResult:
        return ProviderResult(success=True, provider_message_id="mock-email-id")
