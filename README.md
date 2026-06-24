# Athena Voice Agent Tester

A Python voice bot that calls the Pretty Good AI Athena assessment line (+1-805-439-8008) and conducts realistic patient conversations to evaluate agent quality, find bugs, and stress-test edge cases.

## Quick Start

```powershell
# Terminal 1 — API server
cd "E:\Coding-practice\Projects\athena-voice-agent-tester"
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# Terminal 2 — public tunnel
ngrok http --url=uniformed-ooze-applied.ngrok-free.dev 8000

# Terminal 3 — place a call
.\.venv\Scripts\Activate.ps1
python run.py call --scenario 01_schedule_basic --execute
```

## Setup

### Requirements

- Python 3.13
- A Twilio account with one purchased phone number
- An Anthropic API key
- An ngrok account with a static domain

### 1. Create and activate a virtual environment

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your credentials:

```dotenv
ANTHROPIC_API_KEY=your_anthropic_api_key
CLAUDE_CONVERSATION_MODEL=claude-sonnet-4-6
CLAUDE_EVALUATION_MODEL=claude-sonnet-4-6
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx       # your purchased Twilio number
TARGET_PHONE_NUMBER=+18054398008       # do not change this
PUBLIC_BASE_URL=https://your-domain.ngrok-free.dev
RESPONSE_DELAY_MS=500
MAX_CALL_SECONDS=300
```

### 3. Start the API server

```powershell
uvicorn app.main:app --reload --port 8000
```

### 4. Expose the server publicly via ngrok

```powershell
ngrok http --url=your-domain.ngrok-free.dev 8000
```

Make sure `PUBLIC_BASE_URL` in `.env` matches your ngrok domain. Restart uvicorn after any `.env` change.

## Running Calls

### Dry run (no call placed)

```powershell
python run.py call --scenario 01_schedule_basic
```

Confirms the destination number is `+18054398008` and the webhook URLs use your ngrok domain.

### Place a real call

```powershell
python run.py call --scenario 01_schedule_basic --execute
```

### Available scenarios

| File | Scenario |
|------|----------|
| `01_schedule_basic` | Simple appointment scheduling |
| `02_reschedule` | Reschedule an existing appointment |
| `03_cancel` | Cancel an existing appointment |
| `04_refill` | Medication refill request |
| `05_insurance` | Update insurance information |
| `06_office_hours` | Office hours and weekend appointment request |
| `07_unclear_request` | Vague and unclear patient request |
| `08_interruptions` | Barge-in and mid-sentence topic switch |
| `09_conflicting_information` | Conflicting date of birth — identity verification |
| `10_high_risk_edge_case` | Urgent same-day request and distressed patient |

## Outputs

All outputs are written to `outputs/` (excluded from git):

| Directory | Contents |
|-----------|----------|
| `outputs/metadata/` | JSON Lines event log for each call (TwiML, WebSocket events, status callbacks) |
| `outputs/transcripts/` | Human-readable transcript with automated bug analysis |
| `outputs/recordings/` | MP3 dual-channel recording of each call |
| `outputs/bug_reports/` | Per-call bug report extracted from transcript analysis |

## Running Tests

```powershell
pytest -q
```

## Verifying the server

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Architecture

See `docs/architecture.md` for a full explanation of how the system works and the key design decisions.

## Bug Report

See `docs/bug_report.md` for a consolidated report of all bugs found across the 10+ test calls.
