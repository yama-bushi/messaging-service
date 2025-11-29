from enum import Enum
from dataclasses import dataclass
from typing import Optional


class ProviderStatus(str, Enum):
    SUCCESS = "success"
    TEMPORARY_FAILURE = "temporary_failure"   # e.g., 500/503
    RATE_LIMITED = "rate_limited"             # e.g., 429
    PERMANENT_FAILURE = "permanent_failure"   # e.g., 400/403


@dataclass
class ProviderResult:
    status: ProviderStatus
    provider_message_id: Optional[str] = None
    retry_after_seconds: Optional[int] = None  # for 429 cases
    error_message: Optional[str] = None
