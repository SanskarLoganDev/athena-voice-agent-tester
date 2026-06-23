"""FastAPI and ConversationRelay entry points for the smoke test."""

import asyncio
from uuid import uuid4

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from twilio.twiml.voice_response import Connect, ConversationRelay, VoiceResponse

from app.config import get_settings
from app.models import CallEvent
from app.storage import append_call_event

app = FastAPI(title="Athena Voice Agent Tester")

# Two fixed replies used during the smoke test (no Claude involved).
# After both are sent the WebSocket closes cleanly so the call ends
# rather than hanging open until Twilio's hard timeout.
SMOKE_RESPONSES = (
    "I was hoping for sometime next week, preferably in the morning.",
    "Thank you. I need to check my schedule, so I will call back. Goodbye.",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.api_route("/twilio/voice", methods=["GET", "POST"])
async def voice_webhook(request: Request) -> Response:
    """Return TwiML that connects the answered call to ConversationRelay."""

    settings = get_settings()
    call_id = request.query_params.get("call_id", f"smoke-{uuid4().hex[:8]}")
    websocket_url = (
        f"{settings.websocket_base_url}/ws/conversation?call_id={call_id}"
    )

    response = VoiceResponse()
    connect = Connect()

    # Do NOT pass transcription_provider here during the smoke test.
    # Deepgram requires separate Twilio console configuration; omitting it
    # uses Twilio's built-in STT which works out of the box.
    relay = ConversationRelay(
        url=websocket_url,
        welcome_greeting="Hi, I was hoping to schedule a routine appointment for next week.",
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
            payload={"websocket_url": websocket_url},
        )
    )
    return Response(content=str(response), media_type="application/xml")


@app.websocket("/ws/conversation")
async def conversation_socket(websocket: WebSocket) -> None:
    """Run a deterministic two-turn smoke-test conversation without Claude."""

    await websocket.accept()
    call_id = websocket.query_params.get("call_id", f"smoke-{uuid4().hex[:8]}")
    settings = get_settings()
    response_index = 0

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

            # Only act on final prompt events (last=True means the agent
            # finished speaking; partial transcripts have last=False).
            if event_type != "prompt" or not message.get("last", False):
                continue

            # All smoke responses have been sent — close cleanly instead of
            # leaving the WebSocket open and the call hanging.
            if response_index >= len(SMOKE_RESPONSES):
                append_call_event(
                    CallEvent(
                        call_id=call_id,
                        event_type="smoke_complete",
                        payload={"reason": "all responses sent"},
                    )
                )
                await websocket.close()
                return

            # Wait briefly before replying to avoid sounding instant.
            delay_seconds = settings.response_delay_ms / 1000
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

            reply = SMOKE_RESPONSES[response_index]
            response_index += 1

            await websocket.send_json(
                {
                    "type": "text",
                    "token": reply,
                    "last": True,
                    "interruptible": True,
                    "preemptible": False,
                }
            )
            append_call_event(
                CallEvent(
                    call_id=call_id,
                    event_type="patient_reply",
                    payload={"text": reply, "index": response_index},
                )
            )

    except WebSocketDisconnect:
        append_call_event(
            CallEvent(call_id=call_id, event_type="relay_disconnected")
        )


@app.post("/twilio/call-status")
async def call_status(request: Request) -> dict[str, bool]:
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
    form = dict(await request.form())
    call_id = request.query_params.get(
        "call_id", str(form.get("CallSid", "unknown"))
    )
    append_call_event(
        CallEvent(call_id=call_id, event_type="recording_status", payload=form)
    )
    return {"received": True}
