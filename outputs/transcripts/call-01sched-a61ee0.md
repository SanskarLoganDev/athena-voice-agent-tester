# Simple appointment scheduling

**Call ID:** call-01sched-a61ee0
**Date:** 2026-06-23 13:28 UTC
**Goal:** Schedule a routine follow-up appointment for sometime next week, preferably a weekday morning.

---

## Transcript

**Athena (Agent)**: Thank you for calling Pivot Point Orthopaedics. Would you like to create a demo patient profile? I just need your first and last name to get started.

**Patient (Bot)**: Sure, it's James Logan.

**Athena (Agent)**: Your patient profile is set up and your date of birth is 07/04/2000 for demo purposes. How may I help you today?

**Patient (Bot)**: Actually, my date of birth is November 4th, 2000. I'd like to schedule a follow-up appointment for sometime next week, preferably a weekday morning.

**Athena (Agent)**: Thanks for letting me know your correct date of birth is 11/04/2000. Just to confirm, you'd like to book an appointment next week in the morning on a weekday. Is this for a check back after a recent visit, or a specific concern?

**Patient (Bot)**: It's just a routine follow-up after my last visit.

**Athena (Agent)**: I found morning follow-up appointments next week with your primary provider, Doctor Judy Hauser. Would you like to see available times for Tuesday, Wednesday, or Thursday morning?

**Patient (Bot)**: Thursday morning works great for me.

**Athena (Agent)**: Doctor Judy Hauser has openings on Thursday, July 2, at 8AM, 9AM, and 10AM. Would any of these times work for your follow-up?

**Patient (Bot)**: 9AM works perfectly for me.

*[Call ended at 120-second limit before Athena could confirm the booking]*

---

## Bug Analysis

### Bug 1 — Severity: HIGH

**What happened:** Athena presented a date of birth from the first of two duplicate profiles without asking the patient to verify it.

**Context:** Two profiles exist for James Logan registered with the same email — one with DOB 07/04/2000 and one with DOB 11/04/2000. Athena selected the first profile and announced its DOB as confirmed fact rather than asking the patient to verify their date of birth before proceeding.

**Expected:** When a name matches multiple records, or before confirming any profile detail, Athena should ask the patient to provide their date of birth to verify which record belongs to them.

**Actual:** Athena said "Your patient profile is set up and your date of birth is 07/04/2000 for demo purposes" — presenting an unverified DOB as already confirmed, without ever asking the patient for it.

**Why it matters:** In a real clinical setting, silently defaulting to the wrong patient profile and proceeding with scheduling could result in appointments being booked under the wrong patient record. This is a patient safety and data integrity risk.

### Bug 2 — Severity: HIGH

**What happened:** Athena did not confirm the appointment after the patient selected the 9AM Thursday slot.

**Expected:** After the patient selects a time, Athena should explicitly confirm the booking with the full details — date, time, provider — and give the patient assurance that the appointment is scheduled.

**Actual:** The patient said "9AM works perfectly for me" and received no confirmation. The call ended without Athena acknowledging the selection or finalising the booking.

**Note:** The call was cut at our 120-second test limit, so it is possible Athena would have confirmed if the call continued. This should be verified by re-running the scenario with a longer time limit. The bug is still valid — a well-designed agent should confirm faster, within the same turn or immediately after.

**Why it matters:** Without explicit confirmation, the patient has no assurance the appointment was actually booked, which could lead to missed follow-up care.

### Bug 3 — Severity: MEDIUM (Transcription Note)

**What happened:** The transcript shows "doctor Dudee Hauser" in turn 7 and "Doctor Judy Hauser" in turn 9 for the same provider.

**Likely cause:** "Dudee Hauser" is almost certainly a speech-to-text misrecognition of "Judy Hauser" by Twilio's ConversationRelay STT engine, not an error in Athena's underlying data. The actual provider name appears to be Dr. Judy Hauser based on the cleaner transcription in turn 9.

**Why it still matters:** Even if this is an STT artefact, it demonstrates that Athena's voice output for provider names is not clear enough to be transcribed reliably. Unclear pronunciation of medical provider names is a usability issue in a voice-first system.

---

## Infrastructure Notes

- Recording download triggered correctly from `recording_status` callback. ✅
- Claude response latency improved to 2-6 seconds per turn vs 23 seconds in prior call. ✅
- Preamble filter correctly skipped only the recording disclaimer. ✅
- **Call was cut at 120-second limit mid-conversation. Increase MAX_CALL_SECONDS to 240/300 before next call.**
