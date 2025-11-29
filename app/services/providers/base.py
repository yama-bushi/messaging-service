from typing import Protocol, Any, Dict, Optional


class ProviderResult:
    def __init__(self, success: bool, provider_message_id: Optional[str] = None):
        self.success = success
        self.provider_message_id = provider_message_id


class BaseProvider(Protocol):
    def send(self, payload: Dict[str, Any]) -> ProviderResult:
        ...
