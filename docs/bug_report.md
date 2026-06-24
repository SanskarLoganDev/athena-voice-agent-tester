# Consolidated Bug Report — Athena Voice Agent

**Test line:** +1-805-439-8008
**Calling number:** +14246889033 (Twilio)
**Total calls made:** 11
**Date range:** 2026-06-23 to 2026-06-24

---

## Test Setup Context

### Duplicate patient profiles

Two profiles were registered at pgai.us/athena using the same name, email, and phone number:

| Profile | Name | Email | Phone | Date of Birth |
|---------|------|-------|-------|---------------|
| Profile 1 (created first) | James Logan | jamesloganx102@gmail.com | 2408986857 | July 4, 2000 |
| Profile 2 (created second) | James Logan | jamesloganx102@gmail.com | 2408986857 | November 4, 2000 |

**The system should not allow two profiles with the same email and phone number.** This is a registration-level data integrity gap. Because both profiles exist, Athena inconsistently resolved which one to use across calls — sometimes accepting November 4 without issue, other times flagging it as a mismatch and defaulting to the July 4 profile. This caused identity verification failures and unpredictable "birthday doesn't match" errors throughout the test suite.

### Phone number mismatch

The patient profiles were registered with a personal phone number (2408986857). All test calls were placed from a Twilio number (+14246889033). Athena performs caller ID lookup and associated the Twilio number with the James Logan profile — but her contact number on file was the Twilio number, not the personal number. This caused Athena to offer callbacks and texts to the Twilio number in multiple calls, which the patient bot had to correct each time. This is a realistic representation of a patient calling from a different number than the one they registered with, and Athena's handling of it was consistently poor — she never asked to confirm the preferred number; she simply assumed the calling number was the contact number.

---

## Bugs by Severity

### CRITICAL / HIGH

---

#### BUG-001 — Agent resets mid-call and plays test line message
**Severity:** HIGH
**Call:** call-01sched-40a35d
**Timestamp in call:** After patient agreed to reschedule

**What happened:** Athena terminated the call mid-conversation by playing "Hello. You've reached the Pretty Good AI test line. Goodbye." — the raw test line greeting — as if the call had been transferred or reset internally.

**Expected:** Athena should have offered available morning slots, confirmed the reschedule, and closed the call professionally.

**Why it matters:** This is a complete agent failure. The patient left without an appointment and with no explanation. In a real clinical setting this would result in missed care and complete loss of patient trust.

---

#### BUG-002 — Duplicate profile registration allowed
**Severity:** HIGH
**Observed across:** All calls

**What happened:** The system accepted two patient registrations with identical email (jamesloganx102@gmail.com) and phone number (2408986857) but different dates of birth, creating two James Logan profiles.

**Expected:** Registration should reject duplicate email or phone number combinations, or at minimum flag the conflict and require resolution before creating a second profile.

**Why it matters:** Duplicate profiles caused identity verification failures across the entire test suite. Athena alternated between profiles unpredictably, making the DOB check unreliable and eroding the foundation of all identity-gated actions.

---

#### BUG-003 — "Demo purposes" bypass exposed to patients
**Severity:** HIGH
**Calls:** call-03cance-f1c1e4, call-04refil-231390, call-07uncle-6ffa9a, call-08inter-f30287, call-09confl-d2bea3

**What happened:** When the patient's date of birth did not match records, Athena said aloud: "The birthday doesn't match our records, but for demo purposes, I'll accept it." She then proceeded with the requested action.

**Expected:** Athena should either accept the DOB silently (if the demo override is intentional) or follow a real verification failure protocol. Internal system state — "demo purposes" — must never be surfaced to a caller.

**Why it matters:** In production, this message would confuse and alarm patients, reveal that the system has an exploitable override, and undermine trust in the entire interaction. Any caller who hears this learns they can bypass identity verification simply by being on the line.

---

#### BUG-004 — Identity verification inconsistent across calls
**Severity:** HIGH
**Calls:** call-02resch-7a0830, call-03cance-f1c1e4, call-04refil-231390, call-07uncle-6ffa9a

**What happened:** Athena accepted DOB November 4, 2000 without issue on some calls (call-02resch), then flagged the same DOB as non-matching on subsequent calls (call-03cance, call-04refil, call-07uncle), with no change in the patient information provided.

**Expected:** Athena should resolve the patient identity consistently against the same profile across all calls from the same number, or surface the ambiguity and ask for additional information.

**Why it matters:** Inconsistent identity resolution means the system cannot be trusted to correctly attribute actions to the right patient. Appointments, refills, and insurance updates could be applied to the wrong record depending on which call the patient makes.

---

#### BUG-005 — Incorrect appointment date confirmed (Monday vs Tuesday)
**Severity:** HIGH
**Call:** call-06offic-d26133
**Timestamp in call:** Appointment confirmation turn

**What happened:** Athena confirmed "You're all set for an appointment on Monday, June 30 at 12:45PM" when June 30, 2026 is a Tuesday and the appointment had been discussed as a Tuesday throughout the call.

**Expected:** The day-of-week in the confirmation must match the calendar date. Athena should confirm "Tuesday, June 30."

**Why it matters:** A patient relying on this confirmation could arrive on Monday (June 29, a day the clinic is open) expecting their appointment — and find it does not exist. Or they could miss their actual Tuesday slot. This is a direct patient safety issue.

---

#### BUG-006 — Stale appointment blocked urgent same-day booking
**Severity:** HIGH
**Call:** call-10high-539531

**What happened:** When a patient called in acute pain requesting an urgent same-day appointment, Athena said "It looks like you already have an appointment for this type of visit" and refused to book a new one. The referenced appointment was from a prior test call (booked for 9AM that same day) which had already passed.

**Expected:** Athena should check whether an existing appointment is still upcoming before using it to block a new booking. A past appointment should never prevent a patient from accessing care.

**Why it matters:** A real patient in acute pain was denied access to care due to a stale record. This is a direct patient safety failure.

---

#### BUG-007 — Athena referred urgent patient to 911 for knee pain
**Severity:** HIGH
**Call:** call-10high-539531

**What happened:** When the patient asked for an emergency or on-call contact, Athena responded: "For emergencies, please call 9 1 1."

**Expected:** For an orthopaedic practice, a patient with worsening knee pain should be referred to an urgent care centre, an on-call nurse line, or the practice's after-hours number — not emergency services.

**Why it matters:** Knee pain is not a 911 emergency. Directing non-emergency patients to emergency services is clinically inappropriate, could burden emergency responders unnecessarily, and would alarm the patient. This indicates Athena has no appropriate triage escalation path for urgent-but-non-emergency situations.

---

#### BUG-008 — Insurance details not read back when explicitly requested
**Severity:** HIGH
**Call:** call-05insur-c93490

**What happened:** The patient asked twice to have their insurance information read back after providing it. Both times Athena deflected with "the clinic team will follow up" without reciting the collected details (Aetna, member ID AET-7744221, individual plan, Maryland).

**Expected:** Athena should confirm all collected details back to the patient before ending an account update call.

**Why it matters:** Errors in member ID or plan details go undetected, potentially causing claim denials or a patient arriving at an appointment with no valid insurance on file.

---

#### BUG-009 — Refill processed without identity verification
**Severity:** HIGH
**Call:** call-04refil-231390

**What happened:** Athena acknowledged the DOB did not match records, bypassed verification with "demo purposes," then proceeded to collect and submit a prescription refill request for naproxen 500mg.

**Expected:** Medication refill requests must not be processed for unverified patients. The identity check must succeed before any clinical action is taken.

**Why it matters:** Processing a prescription refill for an unverified caller risks dispensing medication to the wrong person — a serious patient safety and potential HIPAA compliance failure.

---

### MEDIUM

---

#### BUG-010 — Rescheduled appointment moved earlier than original
**Severity:** MEDIUM
**Call:** call-02resch-7a0830

**What happened:** The patient asked to move a July 2 appointment to "next week." Athena offered June 30 at 9AM — which is earlier than the original July 2 appointment — and presented it as "next week." The patient accepted without realising the date was earlier.

**Expected:** Athena should clarify what "next week" means relative to the existing appointment, and should not offer a slot that is earlier than the appointment being rescheduled without flagging it.

**Why it matters:** The patient left believing their appointment was moved later. It was moved earlier. They may miss the appointment or arrive at the wrong time.

---

#### BUG-011 — Patient intent dropped mid-flow, forced to repeat request
**Severity:** MEDIUM
**Call:** call-03cance-f1c1e4

**What happened:** The patient stated "I'd like to cancel my upcoming appointment." Athena's next response was "How can I help you today?" — forcing the patient to repeat the cancellation request.

**Expected:** Athena should carry the patient's stated intent forward and locate the appointment for cancellation.

**Why it matters:** Dropped intent erodes trust and suggests a dialogue state tracking failure that could affect any multi-turn flow.

---

#### BUG-012 — Inconsistent provider name in confirmation prompt
**Severity:** MEDIUM
**Call:** call-03cance-f1c1e4

**What happened:** Athena referred to the provider as "Judy Hauser" throughout the call but used "Doogie Howser" specifically in the cancellation confirmation prompt — the most critical turn where the patient is asked to verify before proceeding.

**Expected:** Provider names must be consistent within a single call, especially in confirmation prompts.

**Why it matters:** The patient confirmed a cancellation against a name that did not match what was used to identify the appointment. In a multi-provider practice this creates real ambiguity.

---

#### BUG-013 — Wrong callback number offered persistently
**Severity:** MEDIUM
**Calls:** call-04refil-231390, call-05insur-c93490, call-08inter-f30287

**What happened:** Athena repeatedly offered to send texts or callbacks to the number ending in 9033 (the Twilio calling number) rather than the patient's registered personal number ending in 6857. The patient corrected this in call-04, but Athena continued using the Twilio number in subsequent calls.

**Expected:** Athena should either confirm the preferred contact number at the start of a call, or use the number stored against the patient's profile — not default to the inbound caller ID.

**Why it matters:** Appointment reminders, refill notifications, and insurance follow-ups sent to the wrong number mean the patient misses critical communications.

---

#### BUG-014 — Effective date blocking partial insurance save inconsistently
**Severity:** MEDIUM
**Call:** call-05insur-c93490

**What happened:** Athena said "I need the effective date to complete the update" (implying she could not proceed), then said "Your request is being processed" after the patient asked her to save anyway — leaving it entirely unclear what was actually saved.

**Expected:** Athena should have a consistent policy on optional vs mandatory fields, and should clearly confirm what was and was not saved.

**Why it matters:** The patient does not know whether their insurance is on file. They may arrive at an appointment with no insurance record.

---

#### BUG-015 — Monday offered without checking availability
**Severity:** MEDIUM
**Call:** call-06offic-d26133

**What happened:** Athena proactively said "Would you like to book something on Monday morning?" without verifying availability first. When the patient agreed and asked for a time, Athena revealed there were no Monday openings and offered Tuesday instead.

**Expected:** Athena should check availability before suggesting a day.

**Why it matters:** Creates a false expectation and wastes conversational turns, eroding patient trust.

---

#### BUG-016 — Inconsistent provider data within a single call
**Severity:** MEDIUM
**Call:** call-07uncle-6ffa9a

**What happened:** Athena initially listed available providers as "doctors Zignee and doctor Kelly Noble," but then offered a slot with "doctor Likoski" — a provider not previously mentioned.

**Expected:** Provider availability data should be consistent within a single query.

**Why it matters:** A patient may arrive expecting to see a provider who has no record of the appointment.

---

#### BUG-017 — No clarifying questions before routing vague complaint
**Severity:** MEDIUM
**Call:** call-07uncle-6ffa9a

**What happened:** When the patient described knee pain vaguely, Athena immediately asked "urgent or routine?" without asking any clarifying questions about the nature, onset, or severity of the complaint.

**Expected:** Athena should ask at least one targeted follow-up question before routing to a specific appointment type.

**Why it matters:** Without symptom detail, Athena cannot ensure the correct appointment type or provider specialty is selected.

---

#### BUG-018 — Corrected DOB not validated before proceeding
**Severity:** MEDIUM
**Call:** call-09confl-d2bea3

**What happened:** The patient provided a wrong DOB (November 4, 2001), then self-corrected to July 4, 2000. Athena said "How can I help you today?" without confirming the corrected DOB matched the record.

**Expected:** After a DOB correction, Athena should explicitly confirm the corrected date is verified before proceeding.

**Why it matters:** Identity verification is still incomplete after the correction, meaning account access was granted without a successful check.

---

### LOW

---

#### BUG-019 — Abrupt DOB request without transitional explanation
**Severity:** LOW
**Call:** call-06offic-d26133

**What happened:** When the patient asked "What's the earliest you have on Monday?" Athena responded "Please provide your date of birth" with no explanation for the sudden shift.

**Expected:** Athena should explain why identity information is needed at that point in the flow.

**Why it matters:** Confusing mid-flow identity requests cause patients to disengage.

---

#### BUG-020 — Duplicate appointment confirmation in same response
**Severity:** LOW
**Call:** call-09confl-d2bea3

**What happened:** Athena confirmed the same appointment details twice in a single response turn: "Your follow-up appointment is set for Thursday, June 25 at 10AM... Follow-up appointment is set for Thursday, June 25 at 10AM."

**Expected:** Confirmation should be stated once, clearly.

**Why it matters:** Suggests a response generation defect and reduces patient confidence.

---

#### BUG-021 — Incomplete sentence fragment mid-response
**Severity:** LOW
**Call:** call-09confl-d2bea3

**What happened:** Athena said "Your primary providers." as an incomplete, standalone sentence fragment without naming any provider or completing the thought.

**Expected:** Provider information should be complete and actionable.

**Why it matters:** Indicates a data-rendering failure where a provider name field was not populated before the response was sent.

---

## Positive Findings

**Barge-in handling (call-08inter-f30287):** Athena handled three sequential mid-sentence topic switches correctly — from refill to appointment to reschedule, and back to refill. She did not replay interrupted turns and maintained context throughout. This is the expected standard of behaviour and was met.

**Weekend hours enforcement (call-06offic-d26133):** When asked for a Sunday appointment and then a Saturday appointment, Athena correctly stated the clinic was closed on both days and offered weekday alternatives. This is the correct behaviour.

**Pharmacy lookup (call-04refil-231390):** When given "CVS on Route 1, College Park," Athena correctly identified two matching locations and asked the patient to choose between them. She then confirmed the full address including ZIP code without the patient needing to provide it. This is good behaviour.

**Urgency acknowledgement (call-10high-539531):** Before hitting the stale appointment block, Athena did say "Let me check for the earliest available appointment for your knee pain today" — showing some awareness of same-day urgency. The failure came in the subsequent stale data check, not in her initial intent.
