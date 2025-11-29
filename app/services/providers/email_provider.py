from app.services.providers.base import BaseProvider, ProviderResult

class EmailProvider(BaseProvider):
    def send(self, payload: dict) -> ProviderResult:
        # Mock implementation placeholder
        return ProviderResult(success=True, provider_message_id="mock-email-id")
