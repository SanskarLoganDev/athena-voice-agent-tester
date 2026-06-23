"""Transcript, call metadata, evaluation, and recording persistence."""

import json
from pathlib import Path

from app.models import CallEvent

# Anchor all output paths to the project root (two levels up from this file)
# so they resolve correctly regardless of which directory uvicorn is launched from.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
METADATA_DIRECTORY = _PROJECT_ROOT / "outputs" / "metadata"


def append_call_event(event: CallEvent) -> Path:
    """Append one JSON event to the call's local event log."""

    METADATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = METADATA_DIRECTORY / f"{event.call_id}.jsonl"
    with destination.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event.model_dump(mode="json")) + "\n")
    return destination
