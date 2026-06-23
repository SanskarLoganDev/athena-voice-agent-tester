"""Shared Pydantic data models."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class CallEvent(BaseModel):
    """A locally persisted event from a smoke-test call."""

    call_id: str
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict = Field(default_factory=dict)
