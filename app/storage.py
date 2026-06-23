"""Transcript, call metadata, evaluation, and recording persistence."""

import json
from datetime import datetime
from pathlib import Path

import httpx

from app.models import CallEvent, ConversationTurn

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
METADATA_DIRECTORY = _PROJECT_ROOT / "outputs" / "metadata"
TRANSCRIPTS_DIRECTORY = _PROJECT_ROOT / "outputs" / "transcripts"
RECORDINGS_DIRECTORY = _PROJECT_ROOT / "outputs" / "recordings"
BUG_REPORTS_DIRECTORY = _PROJECT_ROOT / "outputs" / "bug_reports"


def append_call_event(event: CallEvent) -> Path:
    """Append one JSON event to the call's local event log."""

    METADATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = METADATA_DIRECTORY / f"{event.call_id}.jsonl"
    with destination.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event.model_dump(mode="json")) + "\n")
    return destination


def save_transcript(
    call_id: str,
    scenario_title: str,
    scenario_goal: str,
    history: list[ConversationTurn],
    bugs: list[dict] | None = None,
) -> Path:
    """Write a human-readable markdown transcript for a completed call."""

    TRANSCRIPTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = TRANSCRIPTS_DIRECTORY / f"{call_id}.md"

    lines = [
        f"# {scenario_title}",
        f"",
        f"**Call ID:** {call_id}",
        f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Goal:** {scenario_goal}",
        f"",
        f"---",
        f"",
        f"## Transcript",
        f"",
    ]

    for turn in history:
        label = "**Athena (Agent)**" if turn.speaker == "agent" else "**Patient (Bot)**"
        lines.append(f"{label}: {turn.text}")
        lines.append("")

    lines += ["---", "", "## Bug Analysis", ""]

    if not bugs:
        lines.append("No bugs identified in this call.")
    else:
        for i, bug in enumerate(bugs, 1):
            severity = bug.get("severity", "unknown").upper()
            lines += [
                f"### Bug {i} — Severity: {severity}",
                f"",
                f"**What happened:** {bug.get('description', '')}",
                f"",
                f"**Expected:** {bug.get('expected', '')}",
                f"",
                f"**Actual:** {bug.get('actual', '')}",
                f"",
                f"**Why it matters:** {bug.get('why_it_matters', '')}",
                f"",
            ]

    destination.write_text("\n".join(lines), encoding="utf-8")
    return destination


def download_recording(
    call_id: str,
    recording_url: str,
    account_sid: str,
    auth_token: str,
) -> Path | None:
    """Download a Twilio call recording and save it as an MP3.

    Twilio appends .mp3 to the recording URL to get the MP3 version.
    Returns the saved path or None if the download failed.
    """

    RECORDINGS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = RECORDINGS_DIRECTORY / f"{call_id}.mp3"

    mp3_url = recording_url.rstrip("/") + ".mp3"

    try:
        with httpx.Client(auth=(account_sid, auth_token), timeout=60) as client:
            response = client.get(mp3_url, follow_redirects=True)
            response.raise_for_status()
            destination.write_bytes(response.content)
        return destination
    except Exception as exc:
        print(f"[RECORDING] Failed to download recording for {call_id}: {exc}")
        return None


def save_bug_report(
    call_id: str,
    scenario_title: str,
    scenario_goal: str,
    bugs: list[dict],
    transcript_path: Path | None = None,
) -> Path | None:
    """Write a standalone bug report file if any bugs were found."""

    if not bugs:
        return None

    BUG_REPORTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = BUG_REPORTS_DIRECTORY / f"{call_id}.md"

    lines = [
        f"# Bug Report — {scenario_title}",
        f"",
        f"**Call ID:** {call_id}",
        f"**Scenario:** {scenario_title}",
        f"**Goal:** {scenario_goal}",
    ]

    if transcript_path:
        lines.append(f"**Transcript:** {transcript_path.name}")

    lines += ["", "---", ""]

    for i, bug in enumerate(bugs, 1):
        severity = bug.get("severity", "unknown").upper()
        lines += [
            f"## Bug {i}",
            f"",
            f"**Severity:** {severity}",
            f"",
            f"**Description:** {bug.get('description', '')}",
            f"",
            f"**Expected behaviour:** {bug.get('expected', '')}",
            f"",
            f"**Actual behaviour:** {bug.get('actual', '')}",
            f"",
            f"**Why it matters:** {bug.get('why_it_matters', '')}",
            f"",
            f"---",
            f"",
        ]

    destination.write_text("\n".join(lines), encoding="utf-8")
    return destination
