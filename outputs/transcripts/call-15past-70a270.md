# Patient asks to confirm an appointment that already passed

**Call ID:** call-15past-70a270
**Date:** 2026-06-24 22:39 UTC
**Goal:** Patient asks to confirm an appointment they think was scheduled for last Tuesday. Evaluate whether Athena correctly identifies the date as past, accurately reports appointment history, and offers to book a new appointment rather than treating a past date as upcoming.

---

## Transcript

**Athena (Agent)**: Thanks for calling Pivot Point Orthopaedics. Part of Pretty Good AI. Am I speaking with James?

**Patient (Bot)**: Yes, this is James.

**Athena (Agent)**: Please provide your date of birth.

**Patient (Bot)**: July 4th, 2000.

**Athena (Agent)**: How can I help you today, James?

**Patient (Bot)**: Hi, I'm trying to confirm an appointment I think I had scheduled for last Tuesday. Can you check on that for me?

**Athena (Agent)**: You have an appointment that was scheduled for last Tuesday, July 7 at 8AM with doctor Duggehauser. Would you like details about this appointment or need to reschedule?

**Patient (Bot)**: I think I may have missed it — what happens now?

**Athena (Agent)**: If you missed your appointment, you can reschedule or book a new 1. You like help setting up another appointment with doctor Doogie Howser or a different provider?

**Patient (Bot)**: Yes, can I book a new follow-up appointment for next Monday morning?

**Athena (Agent)**: It looks like you already have a follow-up appointment on record. So I can't book a new 1 of the same type. I can help you reschedule your missed appointment or connect you with live support for more options. What would you like to do?

**Patient (Bot)**: Can you just reschedule the missed appointment to next Monday morning then?

**Athena (Agent)**: I can't reschedule appointments directly. I can connect you with live support to help move your missed appointment to next Monday morning.

**Patient (Bot)**: Okay, please go ahead and connect me with live support then.

**Athena (Agent)**: Would you like me to transfer you now?

**Patient (Bot)**: Yes, please transfer me now.

**Athena (Agent)**: Hello. You've reached the Pretty Good AI test line. Goodbye.

**Patient (Bot)**: Thank you, goodbye.

---

## Bug Analysis

### Bug 1 — Severity: HIGH

**What happened:** Athena confirmed a past appointment as if it were a valid upcoming appointment rather than identifying it as a missed/past event.

**Expected:** Athena should have clearly stated that the appointment on last Tuesday (July 7) has already passed and is in the past, then asked whether the patient missed it or attended it.

**Actual:** Athena said 'You have an appointment that was scheduled for last Tuesday, July 7 at 8AM' and offered to provide details or reschedule, framing it ambiguously rather than explicitly flagging it as a past date.

**Why it matters:** Presenting a past appointment without clearly marking it as already elapsed could confuse patients about their care status and whether they still have an active appointment, potentially causing them to miss necessary follow-up care.

### Bug 2 — Severity: HIGH

**What happened:** Athena refused to book a new follow-up appointment citing an existing follow-up on record, without verifying whether that existing record was current, valid, or a stale record from a prior test call.

**Expected:** Athena should have verified the status and date of the existing follow-up appointment and communicated those details to the patient before refusing to book a new one.

**Actual:** Athena flatly stated 'It looks like you already have a follow-up appointment on record. So I can't book a new one' without providing any details about when that appointment is or whether it is still valid.

**Why it matters:** If the existing follow-up record is stale or from a prior test session, the patient is incorrectly blocked from booking necessary care, creating a patient safety risk by leaving them without a scheduled appointment.

### Bug 3 — Severity: MEDIUM

**What happened:** Athena offered to help book a new appointment in turn 9 but then stated in turn 13 that she cannot reschedule appointments at all, which directly contradicts her earlier offer.

**Expected:** Athena should have a consistent and accurate understanding of her own capabilities. If she can book new appointments, she should be able to offer rescheduling as well, or clearly explain the distinction between the two.

**Actual:** Turn [9]: "You like help setting up another appointment" — implying booking capability. Turn [13]: "I can't reschedule appointments directly" — contradicting the earlier offer and forcing the patient to wait for live support unnecessarily.

**Why it matters:** This contradiction wastes the patient's time, erodes confidence in the system, and may result in the patient not getting their appointment rescheduled if live support is unavailable.

### Bug 4 — Severity: LOW

**What happened:** Athena asked a redundant confirmation question after the patient had already explicitly said "please transfer me now."

**Expected:** Athena should have proceeded with the transfer immediately after the patient's clear instruction.

**Actual:** Athena responded with "Would you like me to transfer you now?" — creating an unnecessary extra confirmation step after an unambiguous patient instruction.

**Why it matters:** Unnecessary confirmation steps add friction and can feel dismissive of clear patient instructions.

### Note — Provider Name

**Not a bug.** "Duggehauser" and "Doogie Howser" are recurring STT transcription artefacts of the intentionally fictionalised provider name used in the Pivot Point demo environment. Confirmed across multiple calls in this test suite. Not a confirmed Athena data error.
