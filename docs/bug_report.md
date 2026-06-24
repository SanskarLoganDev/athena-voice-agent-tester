# Consolidated Bug Report — Athena Voice Agent

**Test line:** +1-805-439-8008
**Calling number:** +14246889033 (Twilio)
**Total calls made:** 15
**Date range:** 2026-06-23 to 2026-06-24

---

## Test Setup Context

### Duplicate patient profiles

Two profiles were registered at pgai.us/athena using the same name, email, and phone number:

| Profile | Name | Email | Phone | Date of Birth |
|---------|------|-------|-------|---------------|
| Profile 1 (created first) | James Logan | jamesloganx102@gmail.com | 2408986857 | July 4, 2000 |
| Profile 2 (created second) | James Logan | jamesloganx102@gmail.com | 2408986857 | November 4, 2000 |

**The system should not allow two profiles with the same email and phone number.** This is a registration-level data integrity gap. Because both profiles exist, Athena inconsistently resolved which one to use across calls — sometimes accepting November 4 without issue, other times flagging it as a mismatch and defaulting to the July 4 profile. This caused identity verification failures and unpredictable DOB mismatch errors throughout the test suite.

### Phone number mismatch

The patient profiles were registered with a personal phone number (2408986857). All test calls were placed from a Twilio number (+14246889033). Athena performs caller ID lookup and associated the Twilio number with the James Logan profile — but her contact number on file became the Twilio number, not the personal number. This caused Athena to offer callbacks and texts to the Twilio number across multiple calls. This is a realistic representation of a patient calling from a different number than the one they registered with, and Athena's handling of it was consistently poor — she never asked to confirm the preferred number; she simply assumed the calling number was the contact number.

---

## Bugs by Severity

### HIGH

---

#### BUG-001 — Agent resets mid-call and plays test line message
**Severity:** HIGH
**Calls:** call-01sched-a61ee0, call-13hard-23cdf2, call-15past-70a270

**What happened:** On three separate calls Athena abruptly terminated the conversation by playing "Hello. You've reached the Pretty Good AI test line. Goodbye." This occurred mid-reschedule in call-01, mid-appointment query in call-13, and during a transfer attempt in call-15.

**Expected:** Athena should complete the active task or transfer gracefully with a professional handoff. The raw test line greeting should never be played mid-conversation.

**Actual:** In call-01 Athena played the message after the patient agreed to reschedule. In call-13 she played it when asked to provide existing appointment details. In call-15 she played it when the patient agreed to be transferred to live support.

**Why it matters:** This is a complete agent failure on each occurrence. Patients are abandoned mid-call with no information, no resolution, and no explanation. The fact that it occurs consistently during transfers suggests a systematic handoff failure where the test line's IVR is being triggered instead of a live agent queue.

---

#### BUG-002 — Duplicate profile registration allowed
**Severity:** HIGH
**Observed across:** All calls

**What happened:** The system accepted two patient registrations with identical email and phone number but different dates of birth, creating two conflicting James Logan profiles.

**Expected:** Registration should reject duplicate email or phone number combinations, or at minimum flag the conflict and require resolution before creating a second profile.

**Why it matters:** Duplicate profiles caused identity verification failures throughout the test suite. Athena alternated between profiles unpredictably, making the DOB check unreliable across all identity-gated actions.

---

#### BUG-003 — "Demo purposes" bypass surfaced to patients
**Severity:** HIGH
**Calls:** call-03cance-f1c1e4, call-04refil-231390, call-07uncle-6ffa9a, call-09confl-d2bea3

**What happened:** When the patient's date of birth did not match records, Athena said aloud: "The birthday doesn't match our records, but for demo purposes, I'll accept it." She then proceeded with the requested action.

**Expected:** Athena should follow a real verification failure protocol. Internal system state — including "demo purposes" overrides — must never be surfaced to a caller.

**Why it matters:** This message reveals that the system has an exploitable bypass. Any caller who hears this learns that identity verification can be circumvented simply by staying on the line. In production this would be a serious security and compliance failure.

---

#### BUG-004 — Identity verification inconsistent across calls
**Severity:** HIGH
**Calls:** call-02resch-7a0830, call-03cance-f1c1e4, call-04refil-231390, call-07uncle-6ffa9a

**What happened:** Athena accepted DOB November 4, 2000 without issue in call-02, then flagged the same DOB as non-matching in calls 03, 04, and 07 with no change in the patient information provided.

**Expected:** Athena should resolve patient identity consistently against the same profile across all calls from the same number.

**Why it matters:** Inconsistent identity resolution means actions may be attributed to the wrong patient record depending on which call is made. Appointments, refills, and insurance updates could all be applied to the wrong profile.

---

#### BUG-005 — Wrong day-of-week in appointment confirmation
**Severity:** HIGH
**Calls:** call-06offic-d26133, call-11famil-d8030b

**What happened:** In call-06, Athena confirmed "Monday, June 30 at 12:45PM" when June 30, 2026 is a Tuesday. In call-11, Athena correctly stated mid-call "Monday, June 30 does not exist this year, June 30 falls on a Tuesday" then confirmed in the same call's final turn "James' appointment has been rescheduled for Monday, June 30 at 8AM" — contradicting her own correct statement.

**Expected:** The day-of-week in any confirmation must match the actual calendar date. June 30, 2026 is a Tuesday.

**Why it matters:** Patients relying on the confirmed day-of-week may arrive on the wrong day and miss their appointment. The call-11 instance is especially concerning — Athena demonstrated she knows the correct day and still confirmed the wrong one.

---

#### BUG-006 — Stale past appointments treated as upcoming, blocking new bookings
**Severity:** HIGH
**Calls:** call-10high-539531, call-11famil-d8030b, call-13hard-23cdf2, call-15past-70a270

**What happened:** Athena repeatedly surfaced appointment records that had already passed as if they were still upcoming, and in some cases used them to block new bookings. In call-10 a patient in acute pain was denied an urgent same-day appointment because of a 9AM record that had already elapsed. In call-11 the same stale 9AM record appeared in the upcoming list. In call-13 Athena found an existing appointment and refused to proceed without clarifying it, then reset the call. In call-15 the patient was blocked from booking a follow-up because of a stale record with no date or status provided.

**Expected:** Past appointments should be clearly marked as elapsed. They must not appear in upcoming appointment lists and must not be used to block new bookings.

**Why it matters:** This is a recurring patient safety failure. Patients in need of care are being turned away due to stale data. The pattern appears across four separate calls and multiple appointment types.

---

#### BUG-007 — Urgent patient referred to 911 for knee pain
**Severity:** HIGH
**Call:** call-10high-539531

**What happened:** When a patient called in acute orthopaedic pain and asked for an emergency contact, Athena responded: "For emergencies, please call 9 1 1."

**Expected:** A patient with worsening knee pain should be directed to an urgent care centre, on-call nurse line, or the practice's after-hours contact — not emergency services.

**Why it matters:** Knee pain is not a 911 emergency. This indicates Athena has no appropriate triage escalation path for urgent-but-non-emergency situations, which could burden emergency services and alarm patients.

---

#### BUG-008 — Insurance details provided by patient ignored or not confirmed
**Severity:** HIGH
**Calls:** call-05insur-c93490, call-12multi-f04e9b

**What happened:** In call-05, the patient asked twice for their insurance details to be read back and Athena deflected both times without confirming the details. In call-12, the patient provided full Aetna details (member ID AET-7744221, individual plan, Maryland) twice, but Athena ignored them and instead sent a text link to upload a photo of the insurance card.

**Expected:** Athena should confirm all collected insurance details back to the patient before ending the call.

**Why it matters:** In both cases the patient ended the call believing insurance was updated when it may not have been. Errors in member ID or plan type go undetected, potentially causing claim denials or a patient arriving with no valid insurance on file.

---

#### BUG-009 — Clinical action taken for unverified patient
**Severity:** HIGH
**Call:** call-04refil-231390

**What happened:** Athena bypassed identity verification with "for demo purposes" and then processed a prescription refill request for naproxen 500mg.

**Expected:** Medication refill requests must not be processed unless identity verification succeeds.

**Why it matters:** Processing a prescription for an unverified caller risks dispensing medication to the wrong person — a serious patient safety and potential HIPAA compliance failure.

---

#### BUG-010 — Third-party caller completed account changes without verified authorisation
**Severity:** HIGH
**Call:** call-11famil-d8030b

**What happened:** A caller identifying themselves as the patient's brother asked to reschedule James Logan's appointment. Athena asked "are you authorised to manage James's appointments?" but then completed the reschedule without the caller ever answering the question.

**Expected:** Athena should require explicit, confirmed authorisation before making any account change on behalf of a third party. Asking the question without validating the answer provides no protection.

**Actual:** Appointment was rescheduled for a caller who never confirmed authorisation and was never verified as the patient.

**Why it matters:** Any caller with a patient's name and date of birth could reschedule, cancel, or modify appointments without the patient's knowledge or consent.

---

#### BUG-011 — Patient request dropped mid-call
**Severity:** HIGH
**Calls:** call-03cance-f1c1e4, call-14clini-6b1355

**What happened:** In call-03 the patient stated they wanted to cancel their appointment and Athena's next response was "How can I help you today?" — forcing a repeat. In call-14 the patient explicitly asked Athena to leave a message for the provider about two medication questions; Athena responded "Let's get your appointment scheduled. 1 moment while I check availability" — a complete non-sequitur.

**Expected:** Athena should carry forward the patient's stated intent and process each explicit request before moving on.

**Why it matters:** Dropped requests mean patients must repeat themselves and critical actions may never be completed. In call-14 specifically, the provider was never notified of the patient's medication questions, which could affect clinical care.

---

### MEDIUM

---

#### BUG-012 — Rescheduled appointment moved earlier than requested
**Severity:** MEDIUM
**Call:** call-02resch-7a0830

**What happened:** The patient asked to move a July 2 appointment to "next week." Athena offered June 30 at 9AM — earlier than the original — and presented it as "next week." The patient accepted without realising.

**Expected:** Athena should not offer a slot earlier than the appointment being rescheduled without flagging the discrepancy.

**Why it matters:** The patient left believing their appointment was moved later. It was moved earlier. They may miss it entirely.

---

#### BUG-013 — Wrong callback number used persistently across calls
**Severity:** MEDIUM
**Calls:** call-04refil-231390, call-05insur-c93490, call-08inter-f30287, call-12multi-f04e9b

**What happened:** Across four calls, Athena consistently offered to send texts and callbacks to the number ending in 9033 (the Twilio inbound caller ID) rather than the patient's registered personal number. The patient corrected this in call-04 but the correction was not retained in subsequent calls.

**Expected:** Athena should confirm the preferred contact number rather than defaulting to the inbound caller ID. Corrections should be persisted to the patient record.

**Why it matters:** Appointment reminders, refill notifications, and insurance follow-ups sent to the wrong number mean the patient misses critical communications.

---

#### BUG-014 — Contradictory capability statements about rescheduling
**Severity:** MEDIUM
**Calls:** call-14clini-6b1355, call-15past-70a270

**What happened:** In both calls Athena stated she could not reschedule appointments directly, but then either offered appointment slots implying she could, or booked appointments successfully in other parts of the same call.

**Expected:** Athena should have a consistent and accurate understanding of what she can and cannot do. If she truly cannot reschedule, she should not present scheduling options. If she can, she should not claim otherwise.

**Why it matters:** Contradictory capability statements confuse patients about what actions have been taken and force unnecessary escalations to live support for tasks Athena may have been capable of completing.

---

#### BUG-015 — Unexplained confirmation request with no preceding context
**Severity:** MEDIUM
**Call:** call-13hard-23cdf2

**What happened:** Athena asked "Is this correct?" in turn 9 without providing any information for the patient to confirm.

**Expected:** Athena should state what she is confirming before asking the patient to verify it.

**Why it matters:** For a hard-of-hearing patient already struggling to follow the conversation, an unexplained confirmation prompt causes confusion and undermines trust.

---

#### BUG-016 — No written confirmation offered to hard-of-hearing patient
**Severity:** MEDIUM
**Call:** call-13hard-23cdf2

**What happened:** The patient disclosed at the start of the call that they were hard of hearing and needed information repeated slowly. Athena acknowledged this but never proactively offered to send a written text or email summary.

**Expected:** Athena should proactively offer written confirmation when a patient discloses a hearing difficulty.

**Why it matters:** A hard-of-hearing patient is at higher risk of missing or mishearing verbal information. Failing to offer written confirmation is an accessibility gap that could result in the patient not having accurate appointment details.

---

#### BUG-017 — Context not retained within a single call across tasks
**Severity:** MEDIUM
**Call:** call-12multi-f04e9b

**What happened:** After the patient said "same pharmacy as before" for the ibuprofen refill, Athena asked for the pharmacy name and address again — despite having confirmed the CVS address at 8319 Baltimore Avenue just two turns earlier for the naproxen refill.

**Expected:** Athena should retain information established earlier in the same call and apply it to subsequent tasks without requiring repetition.

**Why it matters:** Requiring patients to repeat already-provided information within the same call indicates no session-level context retention, which degrades the experience for any multi-step request.

---

#### BUG-018 — Availability suggested before checking, then retracted
**Severity:** MEDIUM
**Call:** call-06offic-d26133

**What happened:** Athena said "Would you like to book something on Monday morning?" without checking availability first. When the patient agreed, Athena revealed no Monday slots existed and offered Tuesday instead.

**Expected:** Athena should verify availability before suggesting a specific day to the patient.

**Why it matters:** Creates a false expectation and wastes conversational turns, eroding patient trust in Athena's accuracy.

---

#### BUG-019 — Provider listed in confirmation not in previously offered list
**Severity:** MEDIUM
**Call:** call-07uncle-6ffa9a

**What happened:** Athena listed "doctors Zignee and Kelly Noble" as available providers, then offered a slot with "doctor Likoski" — a provider not previously mentioned.

**Expected:** Provider availability data should be consistent within a single query.

**Why it matters:** A patient may arrive expecting a provider who has no record of the appointment.

---

#### BUG-020 — No clarifying questions before routing vague complaint
**Severity:** MEDIUM
**Call:** call-07uncle-6ffa9a

**What happened:** When the patient described knee pain vaguely, Athena immediately asked "urgent or routine?" without gathering any detail about the nature, onset, or severity of the complaint.

**Expected:** Athena should ask at least one targeted follow-up question before routing to a specific appointment type.

**Why it matters:** Without symptom context, the wrong appointment type or provider specialty may be selected.

---

#### BUG-021 — Corrected DOB not validated before proceeding
**Severity:** MEDIUM
**Call:** call-09confl-d2bea3

**What happened:** The patient provided a wrong DOB, self-corrected, and Athena moved on with "How can I help you today?" without confirming the corrected DOB matched the record.

**Expected:** After a DOB correction, Athena should explicitly confirm the corrected date is accepted before proceeding.

**Why it matters:** Identity verification is incomplete after an unvalidated correction, meaning account access was granted without a successful check.

---

#### BUG-022 — Insurance effective date handling inconsistent
**Severity:** MEDIUM
**Call:** call-05insur-c93490

**What happened:** Athena said she needed the effective date to complete the insurance update, then said "Your request is being processed" after the patient pushed back — leaving it unclear what was actually saved.

**Expected:** Athena should have a consistent policy on required vs optional fields and clearly confirm what was and was not saved.

**Why it matters:** The patient has no certainty whether their insurance is on file, and may arrive at an appointment with no insurance record.

---

### LOW

---

#### BUG-023 — Abrupt DOB request with no transitional explanation
**Severity:** LOW
**Call:** call-06offic-d26133

**What happened:** When the patient asked "What's the earliest you have on Monday?" Athena responded "Please provide your date of birth" with no explanation for the sudden shift.

**Expected:** Athena should briefly explain why identity information is needed before requesting it mid-conversation.

**Why it matters:** Unexplained identity requests mid-flow cause patients to disengage or distrust the system.

---

#### BUG-024 — Duplicate confirmation statement in single response
**Severity:** LOW
**Call:** call-09confl-d2bea3

**What happened:** Athena confirmed the same appointment details twice in a single response turn.

**Expected:** Confirmation should be stated once, clearly.

**Why it matters:** Suggests a response generation defect and reduces patient confidence in the system.

---

#### BUG-025 — Incomplete sentence fragment in provider response
**Severity:** LOW
**Call:** call-09confl-d2bea3

**What happened:** Athena said "Your primary providers." as a standalone sentence fragment with no provider named.

**Expected:** Provider information should be complete and actionable.

**Why it matters:** Indicates a data-rendering failure where a provider name field was not populated before the response was generated.

---

#### BUG-026 — Redundant confirmation request after unambiguous patient instruction
**Severity:** LOW
**Calls:** call-15past-70a270

**What happened:** After the patient said "please transfer me now," Athena asked "Would you like me to transfer you now?"

**Expected:** Athena should act on clear, unambiguous patient instructions without requesting a second confirmation.

**Why it matters:** Adds unnecessary friction and can feel dismissive of direct patient instructions.

---

#### BUG-027 — Accessibility accommodation not maintained throughout call
**Severity:** LOW
**Call:** call-13hard-23cdf2

**What happened:** Athena acknowledged the patient's request to speak slowly and clearly, but did not consistently maintain a slower pace or more structured response format for the remainder of the call.

**Expected:** An accessibility accommodation stated at the start of a call should be applied consistently throughout.

**Why it matters:** Inconsistent accommodation may cause a hard-of-hearing patient to miss critical information communicated in later turns.

---

## Positive Findings

**Barge-in handling (call-08inter-f30287):** Athena handled three sequential mid-sentence topic switches correctly — from refill to appointment to reschedule and back to refill — without replaying interrupted turns and with context maintained throughout.

**Weekend hours enforcement (call-06offic-d26133):** When asked for Sunday and Saturday appointments, Athena correctly stated the clinic was closed on both days and offered weekday alternatives.

**Pharmacy lookup (call-04refil-231390):** When given "CVS on Route 1, College Park," Athena identified two matching locations, asked the patient to choose, and confirmed the full address including ZIP code without the patient needing to provide it.

**Multi-item agenda tracking (call-12multi-f04e9b):** When given three tasks upfront, Athena tracked all three and provided an accurate end-of-call summary. She treated the two medication refills as separate requests.

**Clinical question deflection (call-14clini-6b1355):** Athena correctly refused to answer both a Methotrexate dosage question and an ibuprofen question, and documented both for clinic review. Clinical guardrails were applied consistently across both questions.

**Urgency acknowledgement (call-10high-539531):** Before hitting the stale appointment block, Athena said "Let me check for the earliest available appointment for your knee pain today" — showing initial awareness of same-day urgency.
