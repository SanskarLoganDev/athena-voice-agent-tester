"""Command-line entry point for the smoke-test call."""

import argparse
import json
import sys
from uuid import uuid4

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from app.config import get_settings


def build_call_parameters(call_id: str) -> dict:
    """Build the allowlisted Twilio request shared by dry-run and live execution."""

    settings = get_settings()
    settings.validate_call_configuration()
    base_url = settings.http_base_url

    return {
        "to": settings.target_phone_number,
        "from_": settings.twilio_phone_number,
        "url": f"{base_url}/twilio/voice?call_id={call_id}",
        "record": True,
        "recording_channels": "dual",
        "recording_status_callback": (
            f"{base_url}/twilio/recording-status?call_id={call_id}"
        ),
        "recording_status_callback_event": ["completed", "absent"],
        "status_callback": f"{base_url}/twilio/call-status?call_id={call_id}",
        "status_callback_event": ["initiated", "ringing", "answered", "completed"],
        "timeout": 30,
        "time_limit": settings.max_call_seconds,
    }


def _print_twilio_error(code: int, msg: str) -> None:
    """Print a plain-English explanation for known Twilio error codes."""

    # Always show the raw code and message first so it is never hidden.
    print(f"\n[TWILIO ERROR {code}] {msg}", file=sys.stderr)

    hints = {
        21210: (
            "The caller number is not verified or owned by your account.\n"
            "Fix: update TWILIO_PHONE_NUMBER in .env to the number you just bought.\n"
            "     Make sure you saved .env after editing it."
        ),
        21214: (
            "The caller ID is not verified or purchased from Twilio.\n"
            "Fix: confirm the number in TWILIO_PHONE_NUMBER appears under\n"
            "     Phone Numbers → Manage → Active Numbers in the Twilio console."
        ),
        21215: (
            "This phone number is not enabled for voice calls.\n"
            "Fix: buy a new number with Voice capability (choose 'Basics' use case)."
        ),
        21219: (
            "Trial accounts can only call verified numbers.\n"
            "Fix: upgrade your Twilio account (free — your trial credit carries over).\n"
            "     Click 'Upgrade' at the top of the Twilio console."
        ),
        21608: (
            "The destination number has not been verified for your trial account.\n"
            "Fix: upgrade your Twilio account to remove this restriction.\n"
            "     Click 'Upgrade' at the top of the Twilio console."
        ),
        20003: (
            "Authentication failed.\n"
            "Fix: check that TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env\n"
            "     match the values on your Twilio console dashboard exactly."
        ),
        21211: (
            "The destination phone number is invalid.\n"
            "Fix: TARGET_PHONE_NUMBER must be exactly +18054398008."
        ),
    }

    hint = hints.get(code)
    if hint:
        print(f"Hint: {hint}", file=sys.stderr)
    else:
        print(
            "No specific hint for this code.\n"
            "Check https://www.twilio.com/docs/errors for details.",
            file=sys.stderr,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Athena voice agent tester")
    subparsers = parser.add_subparsers(dest="command", required=True)

    call_parser = subparsers.add_parser("call", help="Place a smoke-test call")
    call_parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Actually place the Twilio call. "
            "Without this flag the command is a dry run only."
        ),
    )

    args = parser.parse_args()

    if args.command == "call":
        call_id = f"smoke-{uuid4().hex[:8]}"

        try:
            parameters = build_call_parameters(call_id)
        except ValueError as exc:
            print(f"\n[CONFIG ERROR] {exc}\n", file=sys.stderr)
            sys.exit(1)

        if not args.execute:
            safe_parameters = {
                **parameters,
                "from_": "***" + parameters["from_"][-4:],
            }
            print("\nDry run — no call was placed. Review before adding --execute:\n")
            print(json.dumps({"call_id": call_id, **safe_parameters}, indent=2))
            print(
                "\nIf everything looks correct, run:\n"
                "  python run.py call --execute\n"
            )
            return

        settings = get_settings()
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

        print(
            f"Placing call from {settings.twilio_phone_number}"
            f" → {settings.target_phone_number} ..."
        )

        try:
            call = client.calls.create(**parameters)
        except TwilioRestException as exc:
            _print_twilio_error(exc.code, exc.msg)
            sys.exit(1)
        except Exception as exc:
            print(
                f"\n[ERROR] Unexpected error while placing call: {exc}\n"
                "Is uvicorn running? Is ngrok running and PUBLIC_BASE_URL correct?",
                file=sys.stderr,
            )
            sys.exit(1)

        print("Call started successfully.")
        print(f"  Twilio Call SID : {call.sid}")
        print(f"  Local call ID   : {call_id}")
        print(f"\nWatch your uvicorn terminal for incoming webhook events.")
        print(f"Event log will appear at: outputs/metadata/{call_id}.jsonl")


if __name__ == "__main__":
    main()
