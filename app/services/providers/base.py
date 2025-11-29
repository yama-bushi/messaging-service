from typing import Protocol, Any

class ProviderResult:
    def __init__(self, success: bool, provider_message_id: str | None = None):
        self.success = success
        self.provider_message_id = provider_message_id

class BaseProvider(Protocol):
    def send(self, payload: dict) -> ProviderResult:
        ...
