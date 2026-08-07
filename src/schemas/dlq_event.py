from time import time
from typing import Any

from pydantic import BaseModel, Field


class DLQEvent(BaseModel):
    """
    Schema for events that failed to process and are routed to the Dead-Letter Queue (DLQ).
    Stores the original payload alongside error metadata for future debugging or replay.
    """

    original_payload: Any = Field(
        ...,
        description="The raw event data that failed to process (dict, string, etc.).",
    )
    error_message: str = Field(
        ...,
        description="The exception message or reason for failure.",
    )
    stack_trace: str | None = Field(
        default=None,
        description="The full stack trace of the exception.",
    )
    source_topic: str = Field(
        ...,
        description="The Kafka topic the event was consumed from (e.g., 'market.crypto').",
    )
    failed_at: float = Field(
        default_factory=time,
        description="UNIX timestamp of when the failure occurred.",
    )
