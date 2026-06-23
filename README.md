# Athena Voice Agent Tester

Python voice bot for testing realistic patient conversations against the
Pretty Good AI Athena assessment line.

## Step 1: Twilio smoke-test call

The first milestone intentionally does not use Claude. It verifies that Twilio
can call the allowlisted assessment number, load TwiML from this application,
open a ConversationRelay WebSocket, play a fixed greeting, exchange two fixed
responses, and record the call.

### Setup

1. Create and activate a virtual environment (Python 3.13 required):

   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and enter the Twilio credentials, the one
   Twilio phone number you will use throughout the challenge, and your public
   HTTPS URL. Do not change `TARGET_PHONE_NUMBER`.

3. Start the API:

   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```

4. In a second terminal, start ngrok (replace with your static domain):

   ```powershell
   ngrok http --url=YOUR-DOMAIN.ngrok-free.dev 8000
   ```

   Set `PUBLIC_BASE_URL=https://YOUR-DOMAIN.ngrok-free.dev` in `.env`.
   Restart uvicorn after updating `.env`.

### Test without making a call

```powershell
Invoke-RestMethod http://localhost:8000/health
python run.py call
pytest -q
```

The call command is a dry run unless `--execute` is supplied. Confirm that its
destination is exactly `+18054398008` and its webhook URLs use your ngrok URL.

You can also inspect the generated TwiML:

```powershell
Invoke-WebRequest "http://localhost:8000/twilio/voice?call_id=manual-test"
```

### Place the smoke-test call

Only after the dry run looks correct:

```powershell
python run.py call --execute
```

Watch the uvicorn and ngrok terminals. After the call, inspect the matching
JSON Lines file under `outputs/metadata/`. It should contain the TwiML request,
ConversationRelay setup and prompt events, the fixed patient replies, call
status events, and a recording-completed event.
