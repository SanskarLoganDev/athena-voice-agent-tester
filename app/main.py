"""FastAPI routes and ConversationRelay WebSocket handler."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from twilio.twiml.voice_response import Connect, ConversationRelay, VoiceResponse

from app.config import get_settings
from app.conversation import analyze_transcript, generate_patient_reply, load_scenario
from app.models import CallEvent, ConversationTurn
from app.storage import (
    append_call_event,
    download_recording,
    save_bug_report,
    save_transcript,
)

app = FastAPI(title="Athena Voice Agent Tester")

# Thread pool for running blocking Claude API calls off the event loop.
# Without this, a 5-10s Claude call blocks the entire WebSocket handler
# and Athena times out waiting, triggering "Are you still there?".
_executor = ThreadPoolExecutor(max_workers=4)

# Lines that are purely legal/admin preamble requiring no reply.
# A line is only skipped if it matches one of these AND contains no question mark.
# This prevents swallowing real questions that happen to start with "thank you".
_PREAMBLE_FRAGMENTS = (
    "this call may be recorded",
    "call may be recorded",
    "recorded for quality",
    "please hold",
    "please wait",
    "connecting you",
    "one moment please",
)


def _is_preamble(text: str) -> bool:
    """Return True only for pure admin/legal lines that need no reply.

    A line with a question mark is never treated as preamble — Athena is
    asking something and the bot must respond.
    """
    if "?" in text:
        return False
    lowered = text.lower()
    return any(fragment in lowered for fragment in _PREAMBLE_FRAGMENTS)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.api_route("/twilio/voice", methods=["GET", "POST"])
async def voice_webhook(request: Request) -> Response:
    """Return TwiML that connects the answered call to ConversationRelay."""

    settings = get_settings()
    call_id = request.query_params.get("call_id", f"call-{uuid4().hex[:8]}")
    scenario_id = request.query_params.get("scenario_id", "01_schedule_basic")
    websocket_url = (
        f"{settings.websocket_base_url}/ws/conversation"
        f"?call_id={call_id}&scenario_id={scenario_id}"
    )

    try:
        scenario = load_scenario(scenario_id)
        greeting = scenario.opening_line or "Hi, I'd like some help please."
    except FileNotFoundError:
        greeting = "Hi, I'd like some help please."

    response = VoiceResponse()
    connect = Connect()
    relay = ConversationRelay(
        url=websocket_url,
        welcome_greeting=greeting,
        language="en-US",
        speech_timeout="800",
        interruptible="speech",
        interrupt_sensitivity="medium",
    )
    connect.append(relay)
    response.append(connect)

    append_call_event(
        CallEvent(
            call_id=call_id,
            event_type="twiml_requested",
            payload={"websocket_url": websocket_url, "scenario_id": scenario_id},
        )
    )
    return Response(content=str(response), media_type="application/xml")


@app.websocket("/ws/conversation")
async def conversation_socket(websocket: WebSocket) -> None:
    """Drive a patient scenario conversation using Claude."""

    await websocket.accept()

    call_id = websocket.query_params.get("call_id", f"call-{uuid4().hex[:8]}")
    scenario_id = websocket.query_params.get("scenario_id", "01_schedule_basic")
    settings = get_settings()

    try:
        scenario = load_scenario(scenario_id)
    except FileNotFoundError as exc:
        append_call_event(
            CallEvent(
                call_id=call_id,
                event_type="scenario_load_error",
                payload={"error": str(exc)},
            )
        )
        await websocket.close()
        return

    history: list[ConversationTurn] = []

    append_call_event(
        CallEvent(
            call_id=call_id,
            event_type="scenario_loaded",
            payload={"scenario_id": scenario_id, "title": scenario.title},
        )
    )

    try:
        while True:
            message = await websocket.receive_json()
            event_type = str(message.get("type", "unknown"))

            append_call_event(
                CallEvent(
                    call_id=call_id,
                    event_type=f"relay_{event_type}",
                    payload=message,
                )
            )

            # Only act when Athena has finished a complete utterance.
            if event_type != "prompt" or not message.get("last", False):
                continue

            agent_text = str(message.get("voicePrompt", "")).strip()
            if not agent_text:
                continue

            # Skip pure legal/admin preamble — but never skip a question.
            if _is_preamble(agent_text):
                append_call_event(
                    CallEvent(
                        call_id=call_id,
                        event_type="preamble_skipped",
                        payload={"text": agent_text},
                    )
                )
                continue

            history.append(ConversationTurn(speaker="agent", text=agent_text))

            # Run Claude in a thread so it does not block the event loop.
            # Blocking the event loop causes Athena to time out and ask
            # "Are you still there?" before the bot has even replied.
            loop = asyncio.get_event_loop()
            try:
                reply, should_end = await loop.run_in_executor(
                    _executor,
                    generate_patient_reply,
                    scenario,
                    list(history),
                )
            except Exception as exc:
                append_call_event(
                    CallEvent(
                        call_id=call_id,
                        event_type="claude_error",
                        payload={"error": str(exc)},
                    )
                )
                await websocket.close()
                return

            # Brief natural pause — keep it short since Claude already took time.
            delay_seconds = settings.response_delay_ms / 1000
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

            history.append(ConversationTurn(speaker="patient", text=reply))

            append_call_event(
                CallEvent(
                    call_id=call_id,
                    event_type="patient_reply",
                    payload={
                        "text": reply,
                        "should_end": should_end,
                        "turn": len(history),
                    },
                )
            )

            await websocket.send_json(
                {
                    "type": "text",
                    "token": reply,
                    "last": True,
                    "interruptible": True,
                    "preemptible": False,
                }
            )

            if should_end:
                await asyncio.sleep(3)
                await websocket.close()
                return

    except WebSocketDisconnect:
        append_call_event(
            CallEvent(call_id=call_id, event_type="relay_disconnected")
        )

    finally:
        if history:
            loop = asyncio.get_event_loop()
            loop.run_in_executor(
                _executor,
                _run_post_call,
                call_id,
                scenario,
                list(history),
                settings,
            )


def _run_post_call(call_id, scenario, history, settings) -> None:
    """Analyse the transcript and save outputs. Runs in a thread."""

    append_call_event(CallEvent(call_id=call_id, event_type="post_call_started"))

    try:
        bugs = analyze_transcript(scenario, history)
    except Exception as exc:
        bugs = []
        append_call_event(
            CallEvent(
                call_id=call_id,
                event_type="analysis_error",
                payload={"error": str(exc)},
            )
        )

    transcript_path = save_transcript(
        call_id=call_id,
        scenario_title=scenario.title,
        scenario_goal=scenario.goal,
        history=history,
        bugs=bugs,
    )

    bug_path = save_bug_report(
        call_id=call_id,
        scenario_title=scenario.title,
        scenario_goal=scenario.goal,
        bugs=bugs,
        transcript_path=transcript_path,
    )

    append_call_event(
        CallEvent(
            call_id=call_id,
            event_type="post_call_complete",
            payload={
                "turns": len(history),
                "bugs_found": len(bugs),
                "transcript": str(transcript_path),
                "bug_report": str(bug_path) if bug_path else None,
            },
        )
    )


@app.post("/twilio/call-status")
async def call_status(request: Request) -> dict[str, bool]:
    """Log call progress events. Does NOT trigger recording download here."""
    form = dict(await request.form())
    call_id = request.query_params.get(
        "call_id", str(form.get("CallSid", "unknown"))
    )
    append_call_event(
        CallEvent(call_id=call_id, event_type="call_status", payload=form)
    )
    return {"received": True}


@app.post("/twilio/recording-status")
async def recording_status(request: Request) -> dict[str, bool]:
    """Download the recording only after Twilio confirms it is fully ready.

    The recording-status callback fires after the call-status callback.
    Downloading from call-status causes a 404 because the file is not
    yet available on Twilio's servers at that point.
    """
    form = dict(await request.form())
    call_id = request.query_params.get(
        "call_id", str(form.get("CallSid", "unknown"))
    )
    append_call_event(
        CallEvent(call_id=call_id, event_type="recording_status", payload=form)
    )

    # Only download when Twilio explicitly says the recording is complete.
    if form.get("RecordingStatus") == "completed":
        recording_url = form.get("RecordingUrl", "")
        if recording_url:
            settings = get_settings()
            loop = asyncio.get_event_loop()
            loop.run_in_executor(
                _executor,
                download_recording,
                call_id,
                recording_url,
                settings.twilio_account_sid,
                settings.twilio_auth_token,
            )

    return {"received": True}
