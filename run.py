"""Command-line entry point for placing scenario calls."""

import argparse
import json
import sys
from uuid import uuid4

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from app.config import get_settings


def build_call_parameters(call_id: str, scenario_id: str) -> dict:
    """Build the Twilio call request parameters."""

    settings = get_settings()
    settings.validate_call_configuration()
    base_url = settings.http_base_url

    return {
        "to": settings.target_phone_number,
        "from_": settings.twilio_phone_number,
        "url": (
            f"{base_url}/twilio/voice"
            f"?call_id={call_id}&scenario_id={scenario_id}"
        ),
        "record": True,
        "recording_channels": "dual",
        "recording_status_callback": (
            f"{base_url}/twilio/recording-status?call_id={call_id}"
        ),
        "recording_status_callback_event": ["completed", "absent"],
        "status_callback": (
            f"{base_url}/twilio/call-status?call_id={call_id}"
        ),
        "status_callback_event": ["initiated", "ringing", "answered", "completed"],
        "timeout": 30,
        "time_limit": settings.max_call_seconds,
    }


def _print_twilio_error(code: int, msg: str) -> None:
    """Print a plain-English explanation for known Twilio error codes."""

    print(f"\n[TWILIO ERROR {code}] {msg}", file=sys.stderr)

    hints = {
        21210: (
            "The caller number is not verified or owned by your account.\n"
            "Fix: update TWILIO_PHONE_NUMBER in .env to the number you bought.\n"
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
            "Fix: upgrade your Twilio account — your trial credit carries over.\n"
            "     Click 'Upgrade' at the top of the Twilio console."
        ),
        21608: (
            "The destination number has not been verified for your trial account.\n"
            "Fix: upgrade your Twilio account to remove this restriction."
        ),
        20003: (
            "Authentication failed.\n"
            "Fix: check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env\n"
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

    call_parser = subparsers.add_parser("call", help="Place a scenario call")
    call_parser.add_argument(
        "--scenario",
        default="01_schedule_basic",
        help=(
            "Scenario file stem to run, e.g. '03_cancel' or '08_interruptions'. "
            "Defaults to 01_schedule_basic."
        ),
    )
    call_parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually place the call. Without this flag the command is a dry run.",
    )

    args = parser.parse_args()

    if args.command == "call":
        scenario_id = args.scenario
        call_id = f"call-{scenario_id[:8].replace('_', '')}-{uuid4().hex[:6]}"

        try:
            parameters = build_call_parameters(call_id, scenario_id)
        except ValueError as exc:
            print(f"\n[CONFIG ERROR] {exc}\n", file=sys.stderr)
            sys.exit(1)

        if not args.execute:
            safe_parameters = {
                **parameters,
                "from_": "***" + parameters["from_"][-4:],
            }
            print(f"\nDry run for scenario: {scenario_id}")
            print("No call was placed. Review before adding --execute:\n")
            print(json.dumps({"call_id": call_id, **safe_parameters}, indent=2))
            print(
                f"\nTo place this call:\n"
                f"  python run.py call --scenario {scenario_id} --execute\n"
            )
            return

        settings = get_settings()
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

        print(f"Scenario  : {scenario_id}")
        print(f"Call ID   : {call_id}")
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
                f"\n[ERROR] Unexpected error: {exc}\n"
                "Is uvicorn running? Is ngrok running and PUBLIC_BASE_URL correct?",
                file=sys.stderr,
            )
            sys.exit(1)

        print("\nCall started successfully.")
        print(f"  Twilio Call SID : {call.sid}")
        print(f"  Local call ID   : {call_id}")
        print(f"\nWatch your uvicorn terminal for live conversation events.")
        print(f"Outputs will appear in:")
        print(f"  outputs/metadata/{call_id}.jsonl")
        print(f"  outputs/transcripts/{call_id}.md")
        print(f"  outputs/recordings/{call_id}.mp3")


if __name__ == "__main__":
    main()
