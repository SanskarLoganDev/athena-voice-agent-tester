"""Tests for local call event persistence."""

import json

from app.models import CallEvent
from app import storage


def test_appends_json_call_event(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(storage, "METADATA_DIRECTORY", tmp_path)

    path = storage.append_call_event(
        CallEvent(call_id="smoke-test", event_type="connected")
    )

    saved = json.loads(path.read_text(encoding="utf-8").strip())
    assert saved["call_id"] == "smoke-test"
    assert saved["event_type"] == "connected"
