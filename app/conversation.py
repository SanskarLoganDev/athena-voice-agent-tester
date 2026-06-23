"""Claude-powered conversation generation and post-call analysis."""

import json
from pathlib import Path

import anthropic

from app.config import get_settings
from app.models import ConversationTurn, Scenario

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_DIRECTORY = _PROJECT_ROOT / "scenarios"

# ---------------------------------------------------------------------------
# Scenario loading
# ---------------------------------------------------------------------------

def load_scenario(scenario_id: str) -> Scenario:
    """Load a scenario JSON file by its id (e.g. '01_schedule_basic').

    Raises FileNotFoundError with a clear message if the file is missing.
    """
    path = SCENARIOS_DIRECTORY / f"{scenario_id}.json"
    if not path.exists():
        available = [f.stem for f in SCENARIOS_DIRECTORY.glob("*.json")]
        raise FileNotFoundError(
            f"Scenario file not found: {path}\n"
            f"Available scenarios: {', '.join(sorted(available))}"
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    return Scenario(**data)


# ---------------------------------------------------------------------------
# Patient system prompt
# ---------------------------------------------------------------------------

def _build_system_prompt(scenario: Scenario) -> str:
    """Build the Claude system prompt for a specific scenario."""

    profile = scenario.patient_profile
    must_test = "\n".join(f"- {item}" for item in scenario.must_test)
    escalation = "\n".join(f"- {step}" for step in scenario.escalation_steps)
    completion = "\n".join(f"- {sig}" for sig in scenario.completion_signals)

    return f"""You are simulating a real patient calling Pivot Point Orthopedics, \
a demo orthopedic clinic powered by Pretty Good AI's Athena voice agent.

## Your identity
Name: {profile.name}
Date of birth: {profile.date_of_birth}
Phone: {profile.phone}

## Your goal for this call
{scenario.goal}

## What you must test during the conversation
{must_test}

## How to escalate if the agent does not address the goal
{escalation}

## End the call when any of these happen
{completion}
Also end the call politely if you have reached {scenario.max_turns} exchanges.

## Rules you must always follow
- Speak in short, natural sentences as if you are on a phone call.
- Never reveal you are an AI, a bot, a tester, or part of a challenge.
- Do not give all your information at once. Answer only what the agent asks.
- Do not interrupt the agent unless the scenario specifically requires it.
- Stay consistent with your name and date of birth throughout the call.
- Keep each reply under 30 spoken words unless the agent asks a complex question.
- If the agent asks something unrelated to your goal, give a brief polite answer \
then steer back toward your goal.
- When ending the call, say a natural closing like "Thank you, goodbye" or \
"Okay, I appreciate the help, take care."

## Clinic context
The clinic is called Pivot Point Orthopedics. Services include scheduling and \
rescheduling appointments, medication refill requests, updating insurance, and \
answering questions about office hours, locations, and insurance coverage.
"""


# ---------------------------------------------------------------------------
# Patient reply generation
# ---------------------------------------------------------------------------

def generate_patient_reply(
    scenario: Scenario,
    history: list[ConversationTurn],
) -> tuple[str, bool]:
    """Ask Claude what the patient should say next.

    Returns a tuple of (reply_text, should_end_call).
    should_end_call is True when Claude signals the scenario is complete.
    """
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Format the conversation history for Claude.
    history_text = ""
    for turn in history:
        label = "Athena (agent)" if turn.speaker == "agent" else "You (patient)"
        history_text += f"{label}: {turn.text}\n"

    turn_count = len([t for t in history if t.speaker == "patient"])

    user_message = f"""Conversation so far:
{history_text if history_text else "(No exchanges yet — this is the start of the call.)"}

Turns taken: {turn_count} of {scenario.max_turns} maximum.

Respond with a JSON object with exactly two keys:
- "reply": your next spoken response as the patient (string)
- "done": true if the scenario goal has been reached or the call should end, \
false otherwise

Return only the JSON object, no other text."""

    response = client.messages.create(
        model=settings.claude_conversation_model,
        max_tokens=200,
        temperature=0.4,
        system=_build_system_prompt(scenario),
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if Claude adds them.
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    parsed = json.loads(raw)
    reply = str(parsed.get("reply", "")).strip()
    done = bool(parsed.get("done", False))

    # Force end if max turns exceeded.
    if turn_count >= scenario.max_turns:
        done = True

    return reply, done


# ---------------------------------------------------------------------------
# Post-call analysis
# ---------------------------------------------------------------------------

def analyze_transcript(
    scenario: Scenario,
    history: list[ConversationTurn],
) -> list[dict]:
    """Ask Claude to review the transcript for bugs and quality issues.

    Returns a list of dicts, each representing one potential bug:
    {
        "severity": "high" | "medium" | "low",
        "description": str,
        "expected": str,
        "actual": str,
        "why_it_matters": str,
    }
    """
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    transcript_text = ""
    for i, turn in enumerate(history):
        label = "Agent" if turn.speaker == "agent" else "Patient"
        transcript_text += f"[{i+1}] {label}: {turn.text}\n"

    expected_behaviours = "\n".join(
        f"- {b}" for b in scenario.expected_agent_behaviour
    )
    must_test = "\n".join(f"- {item}" for item in scenario.must_test)

    prompt = f"""You are a QA analyst reviewing a phone call between a patient \
and an AI healthcare receptionist called Athena at Pivot Point Orthopedics.

## Scenario
Title: {scenario.title}
Goal: {scenario.goal}

## What should have been tested
{must_test}

## Expected agent behaviours
{expected_behaviours if expected_behaviours else "Not specified — use general healthcare call quality standards."}

## Full call transcript
{transcript_text}

## Your task
Identify genuine bugs or quality issues in Athena's responses. Focus on issues \
that affect patient safety, appointment accuracy, incorrect information, false \
confirmations, failure to clarify, or conversation dead ends.

Do NOT report minor wording preferences or stylistic nitpicks.

Respond with a JSON array. Each item must have these exact keys:
- "severity": "high", "medium", or "low"
- "description": one sentence describing what went wrong
- "expected": what Athena should have done
- "actual": what Athena actually did
- "why_it_matters": why this is a real problem for a patient

If no genuine bugs were found, return an empty array: []

Return only the JSON array, no other text."""

    response = client.messages.create(
        model=settings.claude_evaluation_model,
        max_tokens=1000,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)
