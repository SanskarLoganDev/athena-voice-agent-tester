"""Tests for first-step configuration and call construction."""

import re

import pytest

from app.config import ASSESSMENT_NUMBER, Settings, get_settings
from run import build_call_parameters


def test_rejects_any_number_other_than_assessment_number() -> None:
    settings = Settings(
        twilio_account_sid="AC123",
        twilio_auth_token="secret",
        twilio_phone_number="+15551234567",
        target_phone_number="+15550000000",
        public_base_url="https://example.ngrok-free.app",
    )

    with pytest.raises(ValueError, match=re.escape(ASSESSMENT_NUMBER)):
        settings.validate_call_configuration()


def test_builds_recorded_allowlisted_call(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC123")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "secret")
    monkeypatch.setenv("TWILIO_PHONE_NUMBER", "+15551234567")
    monkeypatch.setenv("TARGET_PHONE_NUMBER", ASSESSMENT_NUMBER)
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://example.ngrok-free.app")
    get_settings.cache_clear()

    parameters = build_call_parameters("smoke-test")

    assert parameters["to"] == ASSESSMENT_NUMBER
    assert parameters["record"] is True
    assert parameters["recording_channels"] == "dual"
    assert parameters["url"].endswith("/twilio/voice?call_id=smoke-test")

    get_settings.cache_clear()
