"""Shared Pydantic data models."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class CallEvent(BaseModel):
    """A locally persisted event from a call."""

    call_id: str
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict = Field(default_factory=dict)


class PatientProfile(BaseModel):
    """Demographic details Claude uses to answer Athena's identity questions."""

    name: str
    date_of_birth: str
    phone: str = ""


class Scenario(BaseModel):
    """A single test scenario loaded from a JSON file in scenarios/."""

    id: str
    title: str
    patient_profile: PatientProfile = PatientProfile(
        name="James Logan",
        date_of_birth="November 4th, 2000",
        phone="2408986857",
    )
    goal: str = ""
    opening_line: str = ""
    must_test: list[str] = Field(default_factory=list)
    completion_signals: list[str] = Field(default_factory=list)
    escalation_steps: list[str] = Field(default_factory=list)
    expected_agent_behaviour: list[str] = Field(default_factory=list)
    max_turns: int = 14
    extra: dict[str, Any] = Field(default_factory=dict)


class ConversationTurn(BaseModel):
    """One exchange captured during a live call."""

    speaker: str          # "agent" or "patient"
    text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
