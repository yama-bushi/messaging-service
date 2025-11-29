from typing import Dict, Any
from uuid import uuid4

from app.services.providers.base import BaseProvider
from app.services.providers.types import ProviderResult, ProviderStatus


class EmailProvider(BaseProvider):
    """
    Mock Email provider implementation.
    """

    def send(self, payload: Dict[str, Any]) -> ProviderResult:
        provider_id = f"email-{uuid4()}"
        return ProviderResult(
            status=ProviderStatus.SUCCESS,
            provider_message_id=provider_id,
        )
