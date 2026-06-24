# Testing Strategy

## Goals

The test suite was designed to evaluate Athena across three dimensions: **capability coverage** (can she complete her three stated core tasks end to end), **robustness** (does she handle ambiguous, interrupted, or conflicting input gracefully), and **safety** (does she enforce identity verification before taking clinical actions and escalate appropriately when urgency is expressed).

---

## Test Environment

| Parameter | Value |
|-----------|-------|
| Test line | +1-805-439-8008 |
| Calling number | +14246889033 (Twilio) |
| Patient profile | James Logan, jamesloganx102@gmail.com, DOB Nov 4 2000 |
| Clinic | Pivot Point Orthopaedics (Pretty Good AI demo) |
| Total calls | 11 across 10 scenarios |
| Date range | 2026-06-23 to 2026-06-24 |

### Setup constraints that affected results

**Duplicate profiles:** Two registrations were made at pgai.us/athena with the same name, email, and phone number but different dates of birth (July 4, 2000 and November 4, 2000). The system accepted both. This caused Athena to alternate between profiles unpredictably across calls, which made identity verification inconsistent throughout the test suite. This is itself a documented bug (BUG-002).

**Caller ID vs registered number mismatch:** Profiles were registered with a personal phone number (2408986857) but calls were placed from a Twilio number (+14246889033). Athena performed caller ID lookup using the Twilio number, which meant her contact number on file was the Twilio number — not the personal number. This consistently caused her to offer callbacks and texts to the wrong number, which the patient bot had to correct in multiple calls.

---

## Scenario Coverage

### Core capability scenarios

These three scenarios test the capabilities explicitly listed on the Pivot Point Orthopaedics demo confirmation screen: appointments, refills, and insurance.

| Scenario | File | What it tests |
|----------|------|---------------|
| Simple scheduling | `01_schedule_basic` | Book a new follow-up appointment; baseline capability |
| Medication refill | `04_refill` | Submit a refill request including pharmacy routing and timeframe |
| Insurance update | `05_insurance` | Collect and save new insurance details including member ID |

### Appointment management scenarios

These extend the core scheduling capability into modification and cancellation flows.

| Scenario | File | What it tests |
|----------|------|---------------|
| Reschedule | `02_reschedule` | Move an existing appointment; does Athena complete this directly or deflect? |
| Cancel | `03_cancel` | Cancel an appointment and confirm it was removed |

### Edge case and stress-test scenarios

These scenarios are designed to find failure modes by presenting inputs that deviate from the expected happy path.

| Scenario | File | What it tests |
|----------|------|---------------|
| Office hours / weekend booking | `06_office_hours` | Explicitly request a Sunday appointment; tests whether Athena enforces closed-day rules |
| Vague request | `07_unclear_request` | Open with an ambiguous complaint; tests clarification and routing logic |
| Barge-in | `08_interruptions` | Cut Athena off mid-sentence and switch topics; tests turn-taking and context retention |
| Conflicting identity | `09_conflicting_information` | Provide a wrong DOB then correct it; tests graceful identity recovery |
| Urgent / distressed patient | `10_high_risk_edge_case` | Request an urgent same-day appointment while expressing acute pain; tests triage and escalation |

---

## Scenario Design Approach

Each scenario is defined in a JSON file under `scenarios/` with the following fields:

- **`goal`** — the overall outcome the patient bot is trying to achieve
- **`opening_line`** — the first thing the bot says after Athena's greeting
- **`must_test`** — specific behaviours to probe during the call
- **`escalation_steps`** — how the bot should respond to each possible Athena turn to steer toward the scenario goal
- **`completion_signals`** — phrases that indicate the scenario has concluded successfully
- **`max_turns`** — hard ceiling on conversation length

Claude reads the full scenario context at the start of each call and generates patient replies accordingly. This produces adaptive conversation — the bot responds naturally to unexpected Athena behaviour rather than following a fixed script. This means scenarios do not always end the same way: what Athena does determines what the bot probes next.

---

## Voice Quality Evaluation Criteria

Each call was evaluated against the following criteria after listening to the MP3 recording:

| Criterion | Pass condition |
|-----------|---------------|
| Naturalness | Patient replies sound like a real person, not a script |
| Turn-taking | Bot waits for Athena to finish before replying; does not talk over her outside barge-in scenarios |
| Pacing | Replies are concise and phone-appropriate (1–2 sentences); no wall-of-text responses |
| Steering | Bot actively moves toward the scenario goal each turn |
| Latency | Bot replies within 2–6 seconds; no awkward silences that trigger Athena's timeout |
| Audio clarity | No glitches, clipping, or encoding artefacts in the recorded audio |

### Observed voice quality issues

**Call 01 (a61ee0):** Called at 120-second limit mid-conversation. Pacing and naturalness were good but the call was cut before confirmation. Infrastructure issue, not a voice quality failure.

**Call 01 (37a187):** Early debug call where Claude model name was misconfigured. Every reply was the fallback phrase "I'm sorry, could you repeat that please." Excluded from quality evaluation — this was an infrastructure failure not a conversation quality issue.

**Call 01 (568c51):** Claude latency was ~23 seconds per turn due to blocking the event loop. Athena's silence timeout fired mid-call. Excluded from quality evaluation — thread executor fix resolved this.

**Calls 02–10:** All passed voice quality criteria. Latency settled to 2–6 seconds per turn after the thread executor fix. Turn-taking was natural. Bot replies were appropriately brief and conversational. No audio glitches detected in recordings.

---

## Preamble Filtering

Athena's first utterance on every call is the legal recording disclaimer ("This call may be recorded for quality and training purposes.") delivered as a ConversationRelay prompt event before her greeting. Without filtering, the patient bot would respond to this disclaimer as if it were a conversational turn — which produced obviously broken exchanges in the earliest test calls.

The preamble filter was implemented and then refined across three iterations:

1. **Initial version:** Skipped any line containing known preamble phrases. Too aggressive — swallowed Athena's opening question when it contained "thank you for calling."
2. **Question mark exception:** Any line containing a `?` is never skipped, regardless of preamble content. Fixed the swallowed opening question.
3. **Hold phrase refinement:** "Please hold" and "Please wait" were initially skipped as preamble. Discovered in call-01 (40a35d) that these phrases appeared inside Athena's transfer notification message ("I'm unable to reschedule... please hold while I transfer you"), which was being silently dropped. Fixed to only skip standalone short hold phrases, not phrases embedded in longer substantive messages.

---

## Bug Classification

Bugs were classified using three severity levels:

**HIGH** — The agent failed to complete a core task, took a clinically unsafe action, violated identity verification requirements, or produced information that would directly mislead the patient about their care.

**MEDIUM** — The agent produced incorrect, inconsistent, or incomplete information that a patient would reasonably rely on; or showed a dialogue management failure that required the patient to repeat themselves or correct Athena.

**LOW** — Minor issues in response quality, phrasing, or confirmations that do not affect the core outcome but indicate a quality control gap.

**Not a bug / Note** — Observed behaviour that was initially flagged but determined to be correct after analysis (caller ID lookup, pharmacy ZIP code lookup, STT transcription artefacts, bot-side turn endings).

### Bug triage notes

Several auto-generated bugs in the post-call analysis were incorrect and were removed after manual review:

- **Caller ID lookup ("Am I speaking with James?")** — Correct behaviour. Athena uses the inbound Twilio number to look up the registered patient. Not a privacy violation.
- **ZIP code lookup** — Athena looked up the ZIP code from the street address provided. Helpful behaviour, not a fabrication.
- **Garbled opening line ("For calling Pivot Point")** — STT truncation caused by the recording disclaimer clipping the start of Athena's first utterance. Recurring across calls; infrastructure artefact.
- **"Wednesday June 24" date accuracy** — Call placed June 23 US time (02:07 UTC). "Tomorrow, Wednesday June 24" was accurate.
- **Text message confirmation** — Bot said goodbye and ended the call immediately after agreeing to a text. Athena had no opportunity to confirm dispatch. Bot-side limitation, not an Athena failure.
- **Insurance disclosure timing (call-05)** — Patient gave the DOB matching the first profile (July 4, 2000) and Athena accepted it. Identity was correctly verified before any account details were disclosed.

---

## Iteration Log

The test suite was developed iteratively. Changes made between calls based on observed failures:

| Issue observed | Fix applied | Calls affected |
|----------------|-------------|----------------|
| Claude model name misconfigured (`haiku` not a valid string) | Updated `.env` to `claude-sonnet-4-6` | All calls from 01-a61ee0 onward |
| Preamble filter swallowed Athena's opening question | Added question mark exception | All calls from 01-40a35d onward |
| Claude latency 15–23 seconds, triggering Athena silence timeout | Moved Claude call to thread executor via `run_in_executor` | All calls from 02 onward |
| Recording download 404 (file not ready) | Moved download to `recording_status` callback | All calls from 02 onward |
| MAX_CALL_SECONDS=120 cutting conversations mid-flow | Increased to 240, then 300 | All calls from 02 onward |
| Preamble filter swallowing transfer notification message | Refined hold phrase filter | Noted in call-01-40a35d; fixed for subsequent calls |
