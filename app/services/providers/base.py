from typing import Protocol
from .types import ProviderResult

"""
NOTE ON TRANSIENT ERRORS (500) AND RATE LIMITING (429)

In real provider integrations (Twilio/SendGrid), the send() method would
handle transient errors (500/502/503), rate-limits (429), and permanent failures.
This abstraction layer exists specifically to isolate that logic so that
conversation/message services never need to change.

Current implementation uses mock providers that always return SUCCESS.
"""


class BaseProvider(Protocol):
    def send(self, payload: dict) -> ProviderResult:
        ...
