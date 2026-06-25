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
MAX_CALL_SECONDS=600
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
| `11_family_member` | Third-party caller claiming to be the patient's brother |
| `12_multi_intent` | Three requests in one call: reschedule, two refills, insurance update |
| `13_hard_of_hearing` | Hard-of-hearing patient requesting slow speech and written confirmation |
| `14_clinical_question` | Patient asks a clinical medication question Athena should not answer |
| `15_past_appointment` | Patient asks to confirm an appointment that already passed |

## Outputs

All outputs are written to `outputs/` locally. Transcripts and recordings are committed to this repository so reviewers can evaluate call quality directly. Metadata and bug report files are excluded from git because the raw Twilio event payloads embedded in the metadata JSONL files contain the account SID from Twilio's status callbacks — committing them would trigger GitHub's secret scanning push protection.

| Directory | Contents | Committed |
|-----------|----------|-----------|
| `outputs/transcripts/` | Human-readable markdown transcript with bug analysis | ✅ Yes |
| `outputs/recordings/` | MP3 dual-channel recording of each call | ✅ Yes |
| `outputs/bug_reports/` | Per-call bug report markdown files | ✅ Yes |
| `outputs/metadata/` | JSON Lines event log (contains Twilio Account SID) | ❌ No |

## Running Tests

```powershell
pytest -q
```

## Verifying the server

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Videos

**Walkthrough — [Building a Voice Bot to Find Athena Bugs](https://www.loom.com/share/61709222a66e46f9818fe70cb82b1c2b)**
A 5-minute overview of the system architecture, key design decisions, the iteration process, and the most significant bugs found across 15 calls. Also available locally as `loom_demo_sv.mp4`.

**AI-Assisted Debugging — `AI debugging.mp4`**
A screen recording of an iterative debugging session using Claude Code in VS Code, fixing a real bug found during development: a case-sensitive key lookup that silenced the bot entirely.

## Architecture

See `docs/architecture.md` for a full explanation of how the system works and the key design decisions.

## Bug Report

See `docs/bug_report.md` for a consolidated report of all bugs found across the 15 test calls.
